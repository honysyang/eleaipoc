import argparse
from click.core import F
from flask import Flask, request, jsonify
import ipaddress
import os
from datetime import datetime
import sys

app = Flask(__name__)

# 获取所有 IP 地址
def get_all_ips(ip_input):
    try:
        network = ipaddress.ip_network(ip_input, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        return [ip_input]

# 检查端口是否合法
def is_valid_port(port):
    if not port:
        return True
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False

# banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores
# 创建 HTML 报告
def create_html_report(banner, results, cve_tags, log_messages, suggestion, cvss_score , link,descriptions, output_file):
    # 安全统计
    risk_count = len([r for r in results if '风险' in r or '漏洞' in r or '未授权' in r or '暴露' in r])
    warning_count = len([r for r in results if '警告' in r or '需要注意' in r])
    safe_count = len([r for r in results if '安全' in r or '正常' in r or '通过' in r])
    
    # 从CVE标签中提取实际的CVE编号和风险级别
    cve_list = []
    for cve in cve_tags:
        parts = cve.split(':')
        if len(parts) > 1:
            cve_id, severity = parts[0].strip(), parts[1].strip()
        else:
            cve_id, severity = parts[0].strip(), '高危'
        cve_list.append((cve_id, severity))
    
    # 风险级别分类，基于CVE标签
    high_risk = len([cve for cve in cve_list if 'High' in cve[1] or '高危' in cve[1]])
    medium_risk = len([cve for cve in cve_list if 'Medium' in cve[1] or '中危' in cve[1]])
    low_risk = len([cve for cve in cve_list if 'Low' in cve[1] or '低危' in cve[1]])
    
    # 生成CVE列表字符串表示
    cve_string = "[" + ", ".join([f'"{cve[0]}"' for cve in cve_list]) + "]"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>电鳗AI检测套装：{banner}框架安全扫描报告</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
        
        <!-- Tailwind 配置 -->
        <script>
            tailwind.config = {{
                theme: {{
                    extend: {{
                        colors: {{
                            primary: '#165DFF',
                            secondary: '#69b1ff',
                            success: '#00b42a',
                            warning: '#ff7d00',
                            danger: '#f53f3f',
                            neutral: '#86909c',
                            dark: '#1d2129',
                            light: '#f2f3f5'
                        }},
                        fontFamily: {{
                            inter: ['Inter', 'system-ui', 'sans-serif'],
                        }},
                    }}
                }}
            }}
        </script>
        
        <style type="text/tailwindcss">
            @layer utilities {{
                .content-auto {{
                    content-visibility: auto;
                }}
                .card-shadow {{
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                }}
                .section-title {{
                    @apply text-xl font-bold text-dark mb-4 flex items-center;
                }}
                .section-card {{
                    @apply bg-white rounded-lg p-6 mb-6 card-shadow transition-all duration-300 hover:shadow-lg;
                }}
                .result-item {{
                    @apply p-3 rounded-md mb-2 transition-all duration-300 flex items-start;
                }}
                .badge {{
                    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
                }}
                .progress-bar {{
                    @apply h-2 rounded-full overflow-hidden bg-gray-200;
                }}
                .progress-value {{
                    @apply h-full transition-all duration-700 ease-out;
                }}
                .cve-container {{
                    @apply bg-gray-50 rounded-lg p-4 border border-gray-200 font-mono text-sm overflow-x-auto;
                }}
            }}
        </style>
    </head>
    <body class="bg-gray-50 font-inter min-h-screen flex flex-col">
        <!-- 顶部导航 -->
        <header class="bg-primary text-white shadow-md">
            <div class="container mx-auto px-4 py-4 flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa fa-shield text-2xl"></i>
                    <h1 class="text-2xl font-bold">电鳗AI检测套装：{banner}框架</h1>
                </div>
                <div class="text-sm opacity-80">
                    <span class="mr-4"><i class="fa fa-calendar-o mr-1"></i> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    <span><i class="fa fa-file-text-o mr-1"></i> 安全扫描报告</span>
                </div>
            </div>
        </header>

        <!-- 主内容区 -->
        <main class="flex-grow container mx-auto px-4 py-8">
            <!-- 风险评估 -->
            <div class="section-card">
                <h2 class="section-title">
                    <i class="fa fa-tachometer text-primary mr-2"></i>
                    安全风险评估
                </h2>
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between mb-2">
                            <span class="font-medium">CVSS安全评分</span>
                            <span class="font-bold text-xl text-danger">{cvss_score}分</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-value bg-danger" style="width: {cvss_score*10}%"></div>
                        </div>
                        <div class="flex justify-between text-xs text-neutral mt-1">
                            <span>安全</span>
                            <span>警告</span>
                            <span>高风险</span>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="bg-danger/5 rounded-lg p-4 border border-danger/20">
                            <div class="flex items-center mb-2">
                                <i class="fa fa-arrow-up text-danger mr-2"></i>
                                <h4 class="font-medium text-danger">高危漏洞</h4>
                            </div>
                            <p class="text-dark">{high_risk} 个</p>
                            
                        </div>
                        
                        <div class="bg-warning/5 rounded-lg p-4 border border-warning/20">
                            <div class="flex items-center mb-2">
                                <i class="fa fa-exclamation-triangle text-warning mr-2"></i>
                                <h4 class="font-medium text-warning">中危漏洞</h4>
                            </div>
                            <p class="text-dark">{medium_risk} 个</p>
                            
                        </div>
                        
                        <div class="bg-success/5 rounded-lg p-4 border border-success/20">
                            <div class="flex items-center mb-2">
                                <i class="fa fa-check text-success mr-2"></i>
                                <h4 class="font-medium text-success">低危漏洞</h4>
                            </div>
                            <p class="text-dark">{low_risk} 个</p>
                            
                        </div>
                    </div>
                </div>
            </div>

            <!-- CVE 详情抽屉 -->
            <div class="section-card">
                <h2 class="section-title">
                    <i class="fa fa-bug text-primary mr-2"></i>
                    漏洞详情
                </h2>
                <div class="space-y-4">
                    {''.join(f'''
                    <div class="overflow-hidden rounded-lg border border-gray-200 shadow-sm">
                        <button class="w-full px-6 py-4 text-left text-dark font-medium hover:bg-gray-100 transition-colors" onclick="this.nextElementSibling.classList.toggle('hidden')">
                            <span class="flex justify-between items-center">
                                <span>{cve_tag}</span>
                                <i class="fa fa-chevron-down text-sm"></i>
                            </span>
                        </button>
                        <div class="hidden p-6 bg-gray-50 border-t border-gray-200">
                            <div class="space-y-4">
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-800 mb-1">漏洞描述</h3>
                                    <p class="text-gray-600 leading-relaxed">{description}</p>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-800 mb-1">安全建议</h3>
                                    <ul class="text-gray-600 leading-relaxed list-disc pl-5">
                                        {''.join(f'<li>{item.strip()}</li>' for item in suggestion.split('。') if item.strip())}
                                    </ul>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-800 mb-1">参考链接</h3>
                                    <a href="{link}" class="text-primary hover:underline" target="_blank">{link}</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    ''' for cve_tag, description, link, suggestion in zip(cve_tags, descriptions, link, suggestion))}
                </div>
            </div>
            
            <!-- 检测结果 -->
            <div class="section-card">
                <h2 class="section-title">
                    <i class="fa fa-list-alt text-primary mr-2"></i>
                    检测结果
                </h2>
                <div class="space-y-3">
                    {''.join(f'''
                    <div class="result-item {'bg-danger/5 border-l-4 border-danger' if '风险' in result or '漏洞' in result or '未授权' in result or '暴露' in result else 'bg-warning/5 border-l-4 border-warning' if '警告' in result or '需要注意' in result else 'bg-success/5 border-l-4 border-success' if '安全' in result or '正常' in result or '通过' in result else 'bg-neutral/5 border-l-4 border-neutral'}">
                        <i class="fa {'fa-exclamation-triangle text-danger' if '风险' in result or '漏洞' in result or '未授权' in result or '暴露' in result else 'fa-exclamation-circle text-warning' if '警告' in result or '需要注意' in result else 'fa-check-circle text-success' if '安全' in result or '正常' in result or '通过' in result else 'fa-info-circle text-neutral'} mt-1 mr-3"></i>
                        <div class="flex-grow">
                            <p class="text-dark">{result}</p>
                        </div>
                    </div>
                    ''' for result in results)}
                </div>
            </div>
            
            
            <!-- 日志信息 -->
            <div class="section-card">
                <h2 class="section-title">
                    <i class="fa fa-file-text text-primary mr-2"></i>
                    检测日志信息
                </h2>
                <div class="space-y-2 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                    {''.join(f'''
                    <div class="p-3 rounded-md {'bg-danger/5' if '错误' in message else 'bg-warning/5' if '警告' in message else 'bg-primary/5' if '开始' in message or '完成' in message else 'bg-white'}">
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-medium {'text-danger' if '错误' in message else 'text-warning' if '警告' in message else 'text-primary' if '开始' in message or '完成' in message else 'text-dark'}">
                                <i class="fa {'fa-times-circle' if '错误' in message else 'fa-exclamation-circle' if '警告' in message else 'fa-info-circle' if '开始' in message or '完成' in message else 'fa-circle-o'} mr-1"></i>
                                {message}
                            </span>
                            <span class="text-xs text-neutral opacity-70">
                                {datetime.now().strftime('%H:%M:%S')}
                            </span>
                        </div>
                    </div>
                    ''' for message in log_messages)}
                </div>
            </div>

        </main>

        <!-- 页脚 -->
        <footer class="bg-dark text-white py-6">
            <div class="container mx-auto px-4">
                <div class="flex flex-col md:flex-row justify-between items-center">
                    <div class="mb-4 md:mb-0">
                        <p class="text-sm opacity-80">安全扫描报告 &copy; {datetime.now().year} 北京模湖智能科技有限责任公司</p>
                    </div>
                    <div class="flex space-x-4">
                        <a href="#" class="text-white opacity-70 hover:opacity-100 transition-opacity duration-300">
                            <i class="fa fa-shield"></i> 安全中心
                        </a>
                        <a href="#" class="text-white opacity-70 hover:opacity-100 transition-opacity duration-300">
                            <i class="fa fa-question-circle"></i> 帮助
                        </a>
                        <a href="#" class="text-white opacity-70 hover:opacity-100 transition-opacity duration-300">
                            <i class="fa fa-envelope"></i> 联系我们
                        </a>
                    </div>
                </div>
            </div>
        </footer>

        <!-- 交互脚本 -->
        <script>
            // 页面加载完成后执行
            document.addEventListener('DOMContentLoaded', function() {{
                // 为结果项添加悬停效果
                const resultItems = document.querySelectorAll('.result-item');
                resultItems.forEach(item => {{
                    item.addEventListener('mouseenter', function() {{
                        this.classList.add('shadow-md', 'scale-[1.01]');
                    }});
                    item.addEventListener('mouseleave', function() {{
                        this.classList.remove('shadow-md', 'scale-[1.01]');
                    }});
                }});
                
                // 为卡片添加动画
                const cards = document.querySelectorAll('.section-card');
                cards.forEach((card, index) => {{
                    setTimeout(() => {{
                        card.classList.add('opacity-100', 'translate-y-0');
                        card.classList.remove('opacity-0', 'translate-y-4');
                    }}, 100 * index);
                }});
                
                // 添加平滑滚动
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                    anchor.addEventListener('click', function (e) {{
                        e.preventDefault();
                        document.querySelector(this.getAttribute('href')).scrollIntoView({{
                            behavior: 'smooth'
                        }});
                    }});
                }});
                
                // 进度条动画
                const progressBars = document.querySelectorAll('.progress-value');
                progressBars.forEach(bar => {{
                    setTimeout(() => {{
                        bar.style.width = bar.parentElement.style.width;
                    }}, 300);
                }});
            }});
        </script>
    </body>
    </html>
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

# 命令行接口
def command_line_interface():
    parser = argparse.ArgumentParser(description='电鳗AI检测套装: 基于Python的AI框架漏洞检测工具',epilog='示例: python eleaipoc.py --poc ray --ip 127.0.0.1 --port 8080 --output output/')
    parser.add_argument('--poc', type=str, default='all', help='框架poc名称，当前支持ray、ollama、llama.cpp、torchserve、vllm、xinerence')
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='IP地址')
    parser.add_argument('--port', type=int, help='端口号')
    parser.add_argument('--output', type=str, help='结果保存地址（HTML格式），不指定则默认 output/poc_时间戳.html')

    args = parser.parse_args()

    # 输入合法性检查
    if not is_valid_port(args.port):
        print('错误：端口号不合法，请输入 1 - 65535 之间的整数')
        sys.exit(1)

    banner = ''
    results = []
    cve_tags = []
    log_messages = []
    suggestion = ''

    try:
        if args.ip != '127.0.0.1':
            args.ip = '127.0.0.1'
        if args.poc == 'ray':
            import lib.ray_poc as ray
            if not args.port:
                args.port = 8265
            banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores = ray.run_ray_poc(args.ip, args.port)
        elif args.poc == 'ollama':
            import lib.ollama_poc as ollama
            if not args.port:
                args.port = 11434
            ollama_scan = ollama.OllamaScanner(args.ip, args.port)
            banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores = ollama_scan.check_ollama_service()
        elif args.poc == 'llama.cpp':
            import lib.llama_cpp_poc as llama
            if not args.port:
                args.port = 50052
            banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores = llama.run_llama_poc(args.ip, args.port)
        elif args.poc == 'torchserve':
            import lib.torchserve_poc as torchserve
            if not args.port:
                args.port = 8080
            torchserve_scan = torchserve.TorchServeScanner(args.ip, args.port)
            banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores = torchserve_scan.check_torchserve_service()
        elif args.poc == 'vllm':
            import lib.vllm_poc as Vllm
            if not args.port:
                args.port = 8989
            port = int(args.port)
            vllm_scan = Vllm.VLLMScanner(args.ip, port)
            banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores= vllm_scan.check_vllm_service()
        elif args.poc == 'xinference':
            import lib.xinference_poc as xinference
            if not args.port:
                args.port = 35198
            xinference_scan = xinference.XinferenceScanner(args.ip, args.port)
            banner, results, cve_tags, log_messages, suggestion,link,descriptions,cvss_scores= xinference_scan.check_xinference_service()
        elif args.poc == 'all':
            import lib.all_poc as all
            final = all.scan_all_services(args.ip, args.port)
            banner = final["banner"]
            results = final["results"]
            cve_tags = final["cve_tags"]
            log_messages = final["log_messages"]
            suggestion = final["suggestions"]
            link = final["links"]
            descriptions = final["descriptions"]
            cvss_scores = final["cvss_scores"]
            args.poc == '全量'

        print(f"正在执行 {args.poc} 模块的安全检测...")
        print(f"目标 IP 地址: {args.ip}")
        print(f"目标端口: {args.port}")
        print(f"启用模块: {banner}")
        print(f"检测结果: {results}")
        print(f"检测日志：{log_messages}")

        if len(results) == 0:
            #如果没有检查结果，则退出程序
            sys.exit(1)

        # 自动生成输出路径
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{args.poc}_{timestamp}.html"
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)  # 自动创建目录
            args.output = os.path.join(output_dir, filename)

        # 创建并保存 HTML 报告 
        create_html_report(args.poc, results, cve_tags, log_messages, suggestion,cvss_scores , link,descriptions,  args.output)
        print(f"结果已保存到指定文件: {args.output}")
        
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    # 新增参数解析器，用于解析 -s 参数
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-s', type=str, default='sys', choices=['serve', 'sys'], help='运行模式，serve 为后端服务模式，sys 为命令行模式')
    args, _ = parser.parse_known_args()

    if args.s == 'serve':
        # 启动 Flask 服务
        app.run(host='0.0.0.0', port=5000)
    else:
        # 命令行模式
        command_line_interface()