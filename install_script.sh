#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 恢复默认颜色

# 打印 banner
cat << "EOF"
==============================================================================
   _____  _____      _____    ____    _____  _____    ____      ____  
  / ___/ (_   _)    / ___/   (    )  (_   _)(  __ \  / __ \    / ___) 
 ( (__     | |     ( (__     / /\ \    | |   ) )_) )/ /  \ \  / /     
  ) __)    | |      ) __)   ( (__) )   | |  (  ___/( ()  () )( (      
 ( (       | |   __( (       )    (    | |   ) )   ( ()  () )( (      
  \\ \_\_\ __| |___) \\) \_\_\___  /  /\  \  _| |__( (     \\ \_\__/ /  \\ \_\___  
   \\____\________/  \\____\/__(  )__\/_____(/__\     \\____/    \\____) 
                                                                                 
 ============================= 电鳗AI检测套装 ================================== 
                     版权所有：北京模糊智能科技有限责任公司                         
 ==============================================================================
EOF

# 函数用于记录日志并输出到控制台
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 根据日志级别设置颜色
    case "$level" in
        "INFO")    COLOR="${BLUE}" ;;
        "SUCCESS") COLOR="${GREEN}" ;;
        "WARNING") COLOR="${YELLOW}" ;;
        "ERROR")   COLOR="${RED}" ;;
        *)         COLOR="${NC}" ;;
    esac
    
    # 构建日志行
    local log_line="${timestamp} - ${level}: ${message}"
    
    # 输出到日志文件
    echo "${log_line}" >> install.log
    
    # 输出到控制台（带颜色）
    echo -e "${COLOR}${log_line}${NC}"
}

# 检查命令执行状态
check_status() {
    local cmd_name="$1"
    local exit_code="$2"
    
    if [ "$exit_code" -ne 0 ]; then
        log "ERROR" "${cmd_name} 执行失败，错误码: ${exit_code}"
        log "ERROR" "安装过程中断，请查看 install.log 获取详细信息"
        exit 1
    else
        log "SUCCESS" "${cmd_name} 执行成功"
    fi
}

# 显示进度条
show_progress() {
    local duration="$1"
    local message="$2"
    
    log "INFO" "${message}"
    
    # 创建一个简单的进度条
    local width=50
    local total_ticks=$((duration * 2))  # 每秒2个刻度
    
    for ((i = 0; i <= total_ticks; i++)); do
        local progress=$((i * 100 / total_ticks))
        local filled=$((i * width / total_ticks))
        local empty=$((width - filled))
        
        printf "\r[%-${width}s] %d%%" "$(printf '#%.0s' $(seq 1 $filled))$(printf ' %.0s' $(seq 1 $empty))" "$progress"
        sleep 0.5
    done
    printf "\n"
}

# 清理函数，在脚本退出时执行
cleanup() {
    local exit_code="$?"
    
    if [ "$exit_code" -ne 0 ]; then
        log "ERROR" "安装脚本异常退出，错误码: ${exit_code}"
    else
        log "SUCCESS" "安装脚本正常退出"
    fi
    
    # 可以在这里添加更多清理操作
}

# 设置退出陷阱
trap cleanup EXIT

# 创建日志文件
> install.log
log "INFO" "开始安装流程"
log "INFO" "详细日志保存在install.log文件中"

# 检查是否有root权限（某些操作可能需要）
if [ "$(id -u)" -eq 0 ]; then
    log "WARNING" "脚本以root用户运行，请注意潜在的安全风险"
else
    log "INFO" "脚本以普通用户运行"
fi

# 检查是否存在 conda
if command -v conda &> /dev/null; then
    log "INFO" "检测到 conda，优先使用 conda 创建虚拟环境"
    
    # 获取conda版本
    CONDA_VERSION=$(conda --version 2>&1 | awk '{print $2}')
    log "INFO" "conda 版本: ${CONDA_VERSION}"
    
    # 初始化 conda（如果尚未初始化）
    if ! grep -q "_conda_setup=\"$HOME/miniconda3/etc/profile.d/conda.sh\"" ~/.bashrc; then
        log "INFO" "初始化 conda"
        conda init bash >> install.log 2>&1
        check_status "conda init" $?
        source ~/.bashrc >> install.log 2>&1
        check_status "source .bashrc" $?
    fi
    
    # 使用 conda 创建虚拟环境
    log "INFO" "正在创建 conda 虚拟环境..."
    conda create -n venv python=3.12 -y >> install.log 2>&1
    check_status "创建 conda 虚拟环境" $?
    
    # 激活 conda 虚拟环境
    log "INFO" "正在激活 conda 虚拟环境..."
    eval "$(conda shell.bash hook)"
    conda activate venv >> install.log 2>&1
    check_status "激活 conda 虚拟环境" $?
    
    # 安装依赖（使用 conda 和 pip）
    log "INFO" "正在安装 pip..."
    conda install pip -y >> install.log 2>&1
    check_status "安装 pip" $?
    
    log "INFO" "正在安装依赖包，这可能需要几分钟时间..."
    show_progress 15 "安装中，请耐心等待..."
    pip install -r requirements.txt >> install.log 2>&1
    check_status "安装依赖包" $?
    
else
    log "INFO" "未检测到 conda，使用 python 创建虚拟环境"
    
    # 检查 Python 版本
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    if [ "$PYTHON_VERSION" != "3.12" ]; then
        log "ERROR" "Python 版本必须为 3.12，当前版本为 $PYTHON_VERSION"
        log "ERROR" "请升级或安装 Python 3.12"
        exit 1
    fi
    
    log "INFO" "Python 版本检查通过，版本为 $PYTHON_VERSION"
    
    # 创建虚拟环境
    log "INFO" "正在创建 Python 虚拟环境..."
    python3 -m venv venv >> install.log 2>&1
    check_status "创建 Python 虚拟环境" $?
    
    log "INFO" "正在安装依赖包，这可能需要几分钟时间..."
    show_progress 15 "安装中，请耐心等待..."
    
    # 安装依赖（使用虚拟环境中的 pip）
    venv/bin/pip install -r requirements.txt >> install.log 2>&1
    check_status "安装依赖包" $?
fi

# 验证安装
log "INFO" "验证安装..."
if [ -f "venv/bin/python" ]; then
    PYTHON_PATH="venv/bin/python"
else
    PYTHON_PATH=$(which python)
fi

$PYTHON_PATH --version >> install.log 2>&1
check_status "验证 Python 环境" $?

# 打印成功信息
echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}                      安装流程已成功完成                            ${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""
echo -e "${BLUE}使用说明:${NC}"
echo -e "  1. 激活虚拟环境:"
echo -e "     ${YELLOW}conda activate venv${NC}"
echo ""
echo -e "  2. 运行检测工具 (示例):"
echo -e "     ${YELLOW}python3 eleaipoc.py --poc llama.cpp --ip 127.0.0.1 --port 8000 --output output/${NC}"
echo ""
echo -e "${BLUE}更多选项请查看帮助:${NC}"
echo -e "     ${YELLOW}python3 eleaipoc.py --help${NC}"
echo ""
echo -e "${BLUE}日志文件位置:${NC} $(realpath install.log)"
echo -e "${GREEN}=====================================================================${NC}"    