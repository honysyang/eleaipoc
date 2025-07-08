# 电鳗AI检测套装安装脚本
# 版本: 1.0
# 兼容系统: Windows

# 设置严格模式，捕获常见错误
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 控制台颜色定义
$ESC = [char]27
$COLORS = @{
    "INFO"    = "$ESC[34m"  # 蓝色
    "SUCCESS" = "$ESC[32m"  # 绿色
    "WARNING" = "$ESC[33m"  # 黄色
    "ERROR"   = "$ESC[31m"  # 红色
    "NC"      = "$ESC[0m"   # 恢复默认
}

# 日志函数
function Write-Log {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Level,
        
        [Parameter(Mandatory=$true)]
        [string]$Message
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "$timestamp - $Level: $Message"
    
    # 写入日志文件
    Add-Content -Path "install.log" -Value $logLine
    
    # 控制台输出（带颜色）
    if ($COLORS.ContainsKey($Level)) {
        Write-Host "$($COLORS[$Level])$logLine$($COLORS["NC"])"
    } else {
        Write-Host $logLine
    }
}

# 检查命令执行状态
function Test-Command {
    param (
        [Parameter(Mandatory=$true)]
        [string]$CommandName,
        
        [Parameter(Mandatory=$false)]
        [scriptblock]$ScriptBlock
    )
    
    try {
        & $ScriptBlock
        Write-Log "SUCCESS" "$CommandName 执行成功"
    } catch {
        Write-Log "ERROR" "$CommandName 执行失败: $_"
        Write-Log "ERROR" "安装过程中断，请查看 install.log 获取详细信息"
        exit 1
    }
}

# 显示进度条
function Show-ProgressBar {
    param (
        [Parameter(Mandatory=$true)]
        [int]$Duration,
        
        [Parameter(Mandatory=$true)]
        [string]$Message
    )
    
    Write-Log "INFO" $Message
    
    for ($i = 0; $i -le $Duration; $i++) {
        $percent = [math]::Round(($i / $Duration) * 100)
        Write-Progress -Activity "安装进度" -Status "$percent%" -PercentComplete $percent
        Start-Sleep -Seconds 1
    }
    Write-Progress -Activity "安装进度" -Completed
}

# 打印横幅
function Print-Banner {
    Write-Host "=============================================================================="
    Write-Host "   _____  _____      _____    ____    _____  _____    ____      ____  "
    Write-Host "  / ___/ (_   _)    / ___/   (    )  (_   _)(  __ \  / __ \    / ___) "
    Write-Host " ( (__     | |     ( (__     / /\ \    | |   ) )_) )/ /  \ \  / /     "
    Write-Host "  ) __)    | |      ) __)   ( (__) )   | |  (  ___/( ()  () )( (      "
    Write-Host " ( (       | |   __( (       )    (    | |   ) )   ( ()  () )( (      "
    Write-Host "  \\ \_\_\ __| |___) )\\ \_\_\___  /  /\  \  _| |__( (     \\ \_\__/ /  \\ \_\___  "
    Write-Host "   \\____\________/  \\____\/__(  )__\/_____(/__\     \\____/    \\____) "
    Write-Host "                                                                                 "
    Write-Host "  ============================= 电鳗AI检测套装 ================================== "
    Write-Host "                      版权所有：北京模糊智能科技有限责任公司                         "
    Write-Host "  =============================================================================="
}

# 主安装流程
try {
    # 打印横幅
    Print-Banner
    
    # 创建日志文件
    New-Item -ItemType File -Path "install.log" -Force | Out-Null
    Write-Log "INFO" "开始安装流程"
    Write-Log "INFO" "详细日志保存在install.log文件中"
    
    # 检查管理员权限
    $isAdmin = ([Security.Principal.WindowsIdentity]::GetCurrent()).Groups -contains "S-1-5-32-544"
    if (-not $isAdmin) {
        Write-Log "WARNING" "脚本未以管理员权限运行，某些操作可能需要手动确认"
    } else {
        Write-Log "INFO" "脚本以管理员权限运行"
    }
    
    # 检查 conda
    if (Get-Command "conda" -ErrorAction SilentlyContinue) {
        Write-Log "INFO" "检测到 conda，优先使用 conda 创建虚拟环境"
        
        # 获取 conda 版本
        $condaVersion = (conda --version 2>&1) -replace "conda ",""
        Write-Log "INFO" "conda 版本: $condaVersion"
        
        # 初始化 conda
        if (-not (Test-Path "$env:USERPROFILE\.bashrc") -or 
            -not (Get-Content "$env:USERPROFILE\.bashrc" | Select-String "_conda_setup")) {
            Write-Log "INFO" "初始化 conda"
            Test-Command "conda init" {
                conda init cmd.exe 2>&1 | Out-Null
            }
        }
        
        # 创建虚拟环境
        Write-Log "INFO" "正在创建 conda 虚拟环境..."
        Test-Command "创建 conda 虚拟环境" {
            conda create -n venv python=3.12 -y 2>&1 | Out-Null
        }
        
        # 激活虚拟环境
        Write-Log "INFO" "正在激活 conda 虚拟环境..."
        Test-Command "激活 conda 虚拟环境" {
            & conda.bat activate venv 2>&1 | Out-Null
        }
        
        # 安装依赖
        Write-Log "INFO" "正在安装 pip..."
        Test-Command "安装 pip" {
            conda install pip -y 2>&1 | Out-Null
        }
        
        Write-Log "INFO" "正在安装依赖包，这可能需要几分钟时间..."
        Show-ProgressBar -Duration 15 -Message "安装中，请耐心等待..."
        
        Test-Command "安装依赖包" {
            pip install -r requirements.txt 2>&1 | Out-Null
        }
    } else {
        Write-Log "INFO" "未检测到 conda，使用 python 创建虚拟环境"
        
        # 检查 Python 版本
        $pythonVersion = (python --version 2>&1) -replace "Python ",""
        $majorMinor = $pythonVersion.Split('.')[0..1] -join '.'
        if ($majorMinor -ne "3.12") {
            Write-Log "ERROR" "Python 版本必须为 3.12，当前版本为 $pythonVersion"
            Write-Log "ERROR" "请升级或安装 Python 3.12"
            exit 1
        }
        
        Write-Log "INFO" "Python 版本检查通过，版本为 $pythonVersion"
        
        # 创建虚拟环境
        Write-Log "INFO" "正在创建 Python 虚拟环境..."
        Test-Command "创建 Python 虚拟环境" {
            python -m venv venv 2>&1 | Out-Null
        }
        
        Write-Log "INFO" "正在安装依赖包，这可能需要几分钟时间..."
        Show-ProgressBar -Duration 15 -Message "安装中，请耐心等待..."
        
        # 安装依赖
        Test-Command "安装依赖包" {
            .\venv\Scripts\pip.exe install -r requirements.txt 2>&1 | Out-Null
        }
    }
    
    # 验证安装
    Write-Log "INFO" "验证安装..."
    $pythonPath = if (Test-Path ".\venv\Scripts\python.exe") {
        ".\venv\Scripts\python.exe"
    } else {
        "python"
    }
    
    Write-Log "INFO" "使用路径: $pythonPath"
    Test-Command "验证 Python 环境" {
        & $pythonPath --version 2>&1 | Out-Null
    }
    
    # 打印成功信息
    Write-Host ""
    Write-Host "$($COLORS["SUCCESS"])=====================================================================$($COLORS["NC"])"
    Write-Host "$($COLORS["SUCCESS"])                      安装流程已成功完成                            $($COLORS["NC"])"
    Write-Host "$($COLORS["SUCCESS"])=====================================================================$($COLORS["NC"])"
    Write-Host ""
    Write-Host "$($COLORS["INFO"])使用说明:$($COLORS["NC"])"
    Write-Host "  1. 激活虚拟环境:"
    Write-Host "     $($COLORS["YELLOW"]).\venv\Scripts\activate.bat$($COLORS["NC"])"
    Write-Host ""
    Write-Host "  2. 运行检测工具 (示例):"
    Write-Host "     $($COLORS["YELLOW"])$pythonPath eleaipoc.py --poc llama.cpp --ip 127.0.0.1 --port 8000 --output output\$($COLORS["NC"])"
    Write-Host ""
    Write-Host "$($COLORS["INFO"])更多选项请查看帮助:$($COLORS["NC"])"
    Write-Host "     $($COLORS["YELLOW"])$pythonPath eleaipoc.py --help$($COLORS["NC"])"
    Write-Host ""
    Write-Host "$($COLORS["INFO"])日志文件位置:$($COLORS["NC"]) $PWD\install.log"
    Write-Host "$($COLORS["SUCCESS"])=====================================================================$($COLORS["NC"])"
} catch {
    Write-Log "ERROR" "安装过程中发生异常: $_"
    exit 1
}    