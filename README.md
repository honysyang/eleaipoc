```
==============================================================================
  _____  _____      _____    ____    _____  _____    ____      ____  
 / ___/ (_   _)    / ___/   (    )  (_   _)(  __ \  / __ \    / ___) 
( (__     | |     ( (__     / /\ \    | |   ) )_) )/ /  \ \  / /     
 ) __)    | |      ) __)   ( (__) )   | |  (  ___/( ()  () )( (      
( (       | |   __( (       )    (    | |   ) )   ( ()  () )( (      
 \ \___ __| |___) )\ \_\___  /  /\  \  _| |__( (     \ \_\__/ /  \ \___  
  \____\________/  \____\/__(  )__\/_____(/__\     \____/    \____) 
                                                                                
============================= 电鳗AI检测套装 ==================================
                    版权所有：北京模糊智能科技有限责任公司                          
==============================================================================
```

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
```
git clone https://github.com/honysyang/eleaipoc.git
```

2. 安装环境
    - windows环境(建议管理员权限运行)
    ```
    ./install_script.ps1
    ```

    - linux环境(建议root权限运行)
    ```
    chmod 777 install_script.sh
    ./install_script.sh
    ```
    - 手动安装：
    ```
    python -m venv venv
    source venv/bin/activate 或 venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. 运行漏洞扫描模块
```
source venv/bin/activate 或 venv\Scripts\activate
python eleaipoc.py --poc llama.cpp --ip 127.0.0.1 --port 8000 --output output/
```

## 参数
- --poc: 指定要运行的漏洞扫描模块，支持llama.cpp、Ollama、Ray、Vllm、Xinference、Torchserve、all
- --ip: 指定目标IP地址
- --port: 指定目标端口
- --output: 指定输出目录，默认是当前目录


## 例子
```
python eleaipoc.py --poc llama.cpp --ip 127.0.0.1 --port 8000 --output output/
```
```
(eleaipoc) root@uweic:/home/workspace/pysectool/eleaipoc# python eleaipoc.py --poc ray  --ip 127.0.0.1 --port 8265
```

```

================================================================================
  _____  _____      _____    ____    _____  _____    ____      ____  
 / ___/ (_   _)    / ___/   (    )  (_   _)(  __ \  / __ \    / ___) 
( (__     | |     ( (__     / /\ \    | |   ) )_) )/ /  \ \  / /     
 ) __)    | |      ) __)   ( (__) )   | |  (  ___/( ()  () )( (      
( (       | |   __( (       )    (    | |   ) )   ( ()  () )( (      
 \ \___ __| |___) )\ \_\___  /  /\  \  _| |__( (     \ \_\__/ /  \ \___  
  \____\________/  \____\/__(  )__\/_____(/__\     \____/    \____) 
                                                                                
============================= 电鳗AI检测套装 =====================================
                    版权所有：北京模糊智能科技有限责任公司                          
================================================================================
2025-07-05 00:00:17,630 INFO dashboard_sdk.py:338 -- Uploading package gcs://_ray_pkg_bfc22502c84e31b5.zip.
2025-07-05 00:00:17,630 INFO packaging.py:588 -- Creating a file package for local module './'.
Submitted job ID: raysubmit_LUPspvi8ekxhfU8X
**** 创建job(检测用例)成功，获得job_id为raysubmit_LUPspvi8ekxhfU8X。

检测结果:发现当前Ray框架存在漏洞风险
结果已保存到指定文件: output/ray_20250705000017.html
```
查看检测结果文件：https://github.com/honysyang/eleaipoc/blob/main/output/all_20250708152652.html

![image](https://github.com/user-attachments/assets/93d3f916-1cf9-414e-9913-9616dcbc95b2)


## 声明
本工具为AI框架漏洞检测工具的自查版本，仅用于本地测试和安全评估，不得用于非法或未授权的用途。
此外，我们还具备攻击版本，可用于攻击测试，若用户存在其他需求，可联系我们




