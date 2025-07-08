@echo off

rem 打印 banner
( 
    echo ==============================================================================
    echo    _____  _____      _____    ____    _____  _____    ____      ____  
    echo   / ___/ (_   _)    / ___/   (    )  (_   _)(  __ \  / __ \    / ___) 
    echo  ( (__     | |     ( (__     / /\ \    | |   ) )_) )/ /  \ \  / /     
    echo   ) __)    | |      ) __)   ( (__) )   | |  (  ___/( ()  () )( (      
    echo  ( (       | |   __( (       )    (    | |   ) )   ( ()  () )( (      
    echo   \\ \_\_\ __| |___) )\\ \_\_\___  /  /\  \  _| |__( (     \\ \_\__/ /  \\ \_\___  
    echo    \\____\________/  \\____\/__(  )__\/_____(/__\     \\____/    \\____) 
    echo                                                                                 
    echo  ============================= 电鳗AI检测套装 ================================== 
    echo                      版权所有：北京模糊智能科技有限责任公司                         
    echo  ==============================================================================
)

rem 打印安装开始日志
echo %date% %time% - 开始安装流程 >> install.log

rem 检查 Python 版本
for /f "tokens=2" %%a in ('python --version 2^>^&1') do (
    set PYTHON_VERSION=%%a
)
for /f "delims=. tokens=1,2" %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if not "!PYTHON_MAJOR!.!PYTHON_MINOR!"=="3.12" (
    echo %date% %time% - 错误：Python 版本必须为 3.12，当前版本为 !PYTHON_VERSION! >> install.log
    exit /b 1
)

echo %date% %time% - Python 版本检查通过，版本为 !PYTHON_VERSION! >> install.log

rem 创建虚拟环境
python -m venv venv >> install.log 2>&1
if %%errorlevel%% neq 0 (
    echo %date% %time% - 错误：创建虚拟环境失败 >> install.log
    exit /b 1
)

echo %date% %time% - 虚拟环境创建成功 >> install.log

rem 激活虚拟环境
call venv\\Scripts\\activate.bat >> install.log 2>&1

echo %date% %time% - 虚拟环境激活成功 >> install.log

rem 安装依赖
pip install -r requirements.txt >> install.log 2>&1
if %%errorlevel%% neq 0 (
    echo %date% %time% - 错误：安装依赖失败 >> install.log
    exit /b 1
)

echo %date% %time% - 依赖安装成功 >> install.log

echo %date% %time% - 安装流程完成 >> install.log