![image](https://github.com/user-attachments/assets/0c706f80-c997-4a0e-9d5c-e59d3819a274)


## 名称
电鳗AI检测套装

## 版本
v1.0.0

## 简介
电鳗AI检测套装是一个用于AI框架漏洞检测的工具集合，包含多个高危漏洞检测模块。

## 框架
- llama.cpp
- Ollama
- Ray
- Vllm
- Xinference
- Torchserve

## 环境
- Python 3.12 或 conda

## 文件结构
- eleaipoc.py: 主程序，用于运行漏洞扫描模块
- install_scrip.sh: linux环境下自动安装脚本
- install_script.ps1: windows环境下自动安装脚本
- requirements.txt: 项目依赖文件
- lib/: 漏洞扫描模块


## 使用方法
1. 克隆项目
bash'''
git clone https://github.com/eleaipoc/eleaipoc.git
'''

2. 安装环境
自动化脚本安装：
windows环境(建议管理员权限运行)
bash'''
cmd:./install_script.ps1
'''

linux环境(建议root权限运行)
bash'''
chmod 777 install_script.sh
./install_script.sh
'''

手动安装：
bash'''
python -m venv venv
source venv/bin/activate 或 venv\Scripts\activate
pip install -r requirements.txt
'''

3. 运行漏洞扫描模块
bash'''
source venv/bin/activate 或 venv\Scripts\activate
python eleaipoc.py --poc llama.cpp --ip 127.0.0.1 --port 8000 --output output/
'''

## 参数
- --poc: 指定要运行的漏洞扫描模块，支持llama.cpp、Ollama、Ray、Vllm、Xinference、Torchserve、all
- --ip: 指定目标IP地址
- --port: 指定目标端口
- --output: 指定输出目录，默认是当前目录


## 例子
bash'''
python eleaipoc.py --poc llama.cpp --ip 127.0.0.1 --port 8000 --output output/
'''
![image](https://github.com/user-attachments/assets/143d45e8-92f9-4a51-a06f-b6853be94dd3)


## 声明
本工具为AI框架漏洞检测工具的自查版本，仅用于本地测试和安全评估，不得用于非法或未授权的用途。
此外，我们还具备攻击版本，可用于攻击测试，若用户存在其他需求，可联系我们



