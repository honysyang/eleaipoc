import argparse
import traceback
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
from datetime import datetime

def create_html_report(ip, port, poc, results, cve_tags, log_messages, suggestion, cvss_score, link, descriptions, key_message,output_file):
    """生成符合样式规范的安全扫描HTML报告"""
    # 安全统计：按风险级别分类漏洞
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    cve_list = []
    for cve in cve_tags:
        # 从CVE标签提取风险级别（支持中文/英文描述）
        severity = "高危"
        if "低危" in cve or "Low" in cve:
            severity = "低危"
            low_risk += 1
        elif "中危" in cve or "Medium" in cve:
            severity = "中危"
            medium_risk += 1
        else:
            high_risk += 1
        cve_list.append((cve, severity))

    # 处理建议列表（确保为可迭代格式）
    if isinstance(suggestion, list):
        suggestions = suggestion
    else:
        suggestions = [suggestion] if suggestion else []

    # JavaScript代码作为字符串处理，避免Python解析错误
    js_code = """
    document.addEventListener('DOMContentLoaded', function() {
        // 卡片动画
        const cards = document.querySelectorAll('.section-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(10px)';
            card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * index);
        });

        // 进度条动画
        const progressBars = document.querySelectorAll('.progress-value');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 300);
        });

        // 抽屉式弹窗控制
        const drawerButtons = document.querySelectorAll('[onclick*="classList.toggle(\'open\')"]');
        drawerButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // 阻止事件冒泡到文档
                e.stopPropagation();
            });
        });

        // 关闭按钮和遮罩层点击事件
        document.getElementById('drawer-overlay').addEventListener('click', closeAllDrawers);
        document.querySelectorAll('.drawer-close').forEach(button => {
            button.addEventListener('click', closeAllDrawers);
        });

        function closeAllDrawers() {
            document.getElementById('drawer-overlay').style.display = 'none';
            document.querySelectorAll('.drawer').forEach(drawer => {
                drawer.classList.remove('open');
            });
        }
    });
    """

    # 按风险级别筛选漏洞详情
    high_risk_details = []
    medium_risk_details = []
    low_risk_details = []
    
    # print(suggestions)
    # print(cve_list)
    # print(key_message)
    for i, (cve, severity) in enumerate(cve_list):
        detail_html = f'''
                <button class="collapse-btn" onclick="this.nextElementSibling.classList.toggle('open')">
            <span class="font-semibold text-lg">{cve}</span>
            <span class="transition-transform duration-300">
                <i class="fa fa-chevron-down"></i>
            </span>
        </button>
        <div class="collapse-content">
            <div class="space-y-3">
                <div>
                    <h4 class="font-medium text-gray-700 mb-1">漏洞描述</h4>
                    <p class="text-gray-600">{descriptions[i]}</p>
                </div>
                <div>
                    <h4 class="font-medium text-gray-700 mb-1">扫描特征</h4>
                    <p class="text-gray-600 break-words">{key_message[i]}</p>
                </div>
                <div>
                    <h4 class="font-medium text-gray-700 mb-1">安全建议</h4>
                    <ul class="text-gray-600 list-disc pl-5">
                        {''.join(f'<li>{item.strip()}</li>' for item in (suggestions[i].split('。') if isinstance(suggestions[i], str) else suggestions[i]) if item.strip())}
                    </ul>
                </div>
                <div>
                    <h4 class="font-medium text-gray-700 mb-1">参考链接</h4>
                    <a href="{link[i]}" class="text-primary hover:underline" target="_blank">{link[i]}</a>
                </div>
            </div>
        </div>
        '''
        if severity == '高危':
            high_risk_details.append(detail_html)
        elif severity == '中危':
            medium_risk_details.append(detail_html)
        else:
            low_risk_details.append(detail_html)

    # 生成HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>电鳗AI检测套装：{poc}安全扫描报告</title>
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
            .collapse-btn {{
                @apply flex items-center justify-between w-full py-2 px-4 bg-gray-100 rounded-t-lg cursor-pointer;
            }}
            .collapse-content {{
                @apply hidden p-4 bg-gray-50 rounded-b-lg border border-t-0 border-gray-200;
            }}
            .collapse-content.open {{
                @apply block;
            }}
            /* 抽屉样式 */
            .drawer-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                display: none;
            }}
            .drawer {{
                position: fixed;
                top: 0;
                right: -100%;
                width: 50%;
                max-width: 50%;
                height: 100vh;
                background-color: white;
                box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
                z-index: 1001;
                transition: right 0.3s ease-in-out;
                overflow-y: auto;
            }}
            .drawer.open {{
                right: 0;
            }}
            .drawer-close {{
                position: absolute;
                top: 1rem;
                right: 1rem;
                cursor: pointer;
                font-size: 1.5rem;
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
                <h1 class="text-2xl font-bold">电鳗AI检测套装：蓝队专用</h1>
            </div>
            <div class="text-sm opacity-80">
                <span class="mr-4"><i class="fa fa-calendar-o mr-1"></i> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                <span><i class="fa fa-file-text-o mr-1"></i> 安全扫描报告</span>
            </div>
        </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-grow container mx-auto px-4 py-8">
        <!-- 基本信息 -->
        <div class="section-card">
            <h2 class="section-title">
                <i class="fa fa-info-circle text-primary mr-2"></i>
                基本信息
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- 目标信息 -->
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-100 transform transition-all duration-300 hover:shadow-md">
                    <h4 class="font-medium text-dark mb-3 flex items-center">
                        <i class="fa fa-info-circle text-primary mr-2"></i>
                        目标信息
                    </h4>
                    <ul class="space-y-3">
                        <li class="flex items-center">
                            <span class="w-24 text-neutral">IP地址：</span>
                            <span class="font-medium">{ip}</span>
                        </li>
                        <li class="flex items-center">
                            <span class="w-24 text-neutral">端口：</span>
                            <span class="font-medium">{port if port is not None else "默认端口"}</span>
                        </li>
                    </ul>
                </div>
                
                <!-- 扫描方式 -->
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-100 transform transition-all duration-300 hover:shadow-md">
                    <h4 class="font-medium text-dark mb-3 flex items-center">
                        <i class="fa fa-cogs text-secondary mr-2"></i>
                        扫描方式
                    </h4>
                    <ul class="space-y-3">
                        <li class="flex items-center">
                            <span class="w-24 text-neutral">扫描框架：</span>
                            <span class="font-medium">{'全量扫描' if poc == 'all' else poc }</span>
                        </li>
                        <li class="flex items-center">
                            <span class="w-24 text-neutral">扫描时间：</span>
                            <span class="font-medium">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </li>
                    </ul>
                </div>
                
                <!-- 检测结果 -->
                <div class="bg-gray-50 p-5 rounded-lg border border-gray-100 transform transition-all duration-300 hover:shadow-md">
                    <h4 class="font-medium text-dark mb-3 flex items-center">
                        <i class="fa fa-exclamation-triangle text-warning mr-2"></i>
                        检测结果
                    </h4>
                    <ul class="list-disc list-inside pl-5">
                        {''.join(f'<li>{result}</li>' for result in results)}
                    </ul>
                </div>
            </div>
        </div>
                
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
                        <span class="font-bold text-xl { 'text-danger' if cvss_score >= 7 else 'text-warning' if cvss_score >= 4 else 'text-success' }">
                            {cvss_score}分
                        </span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-value { 'bg-danger' if cvss_score >= 7 else 'bg-warning' if cvss_score >= 4 else 'bg-success' }" 
                             style="width: {min(cvss_score * 10, 100)}%"></div>
                    </div>
                    <div class="flex justify-between text-xs text-neutral mt-1">
                        <span>安全</span>
                        <span>警告</span>
                        <span>高风险</span>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button onclick="document.getElementById('high-risk-details').classList.toggle('open'); document.getElementById('drawer-overlay').style.display = 'block';" 
                            class="bg-danger/5 rounded-lg p-4 border border-danger/20 hover:bg-danger/10 transition-colors">
                        <div class="flex items-center mb-2">
                            <i class="fa fa-arrow-up text-danger mr-2"></i>
                            <h4 class="font-medium text-danger">高危漏洞</h4>
                        </div>
                        <p class="text-dark font-bold">{high_risk} 个</p>
                    </button>
                    
                    <button onclick="document.getElementById('medium-risk-details').classList.toggle('open'); document.getElementById('drawer-overlay').style.display = 'block';" 
                            class="bg-warning/5 rounded-lg p-4 border border-warning/20 hover:bg-warning/10 transition-colors">
                        <div class="flex items-center mb-2">
                            <i class="fa fa-exclamation-triangle text-warning mr-2"></i>
                            <h4 class="font-medium text-warning">中危漏洞</h4>
                        </div>
                        <p class="text-dark font-bold">{medium_risk} 个</p>
                    </button>
                    
                    <button onclick="document.getElementById('low-risk-details').classList.toggle('open'); document.getElementById('drawer-overlay').style.display = 'block';" 
                            class="bg-success/5 rounded-lg p-4 border border-success/20 hover:bg-success/10 transition-colors">
                        <div class="flex items-center mb-2">
                            <i class="fa fa-check text-success mr-2"></i>
                            <h4 class="font-medium text-success">低危漏洞</h4>
                        </div>
                        <p class="text-dark font-bold">{low_risk} 个</p>
                    </button>
                </div>
            </div>
        </div>
        
        <!-- 检测日志 -->
        <div class="section-card">
            <h2 class="section-title">
                <i class="fa fa-file-text text-primary mr-2"></i>
                检测日志信息
            </h2>
            <div class="space-y-2 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                {''.join(f'''
                <div class="p-3 rounded-md mb-2 {
                    'bg-danger/5 border border-danger/20' if '错误' in msg or '失败' in msg else
                    'bg-warning/5 border border-warning/20' if '警告' in msg or '风险' in msg else
                    'bg-success/5 border border-success/20' if '成功' in msg or '完成' in msg else
                    'bg-white'
                }">
                    <div class="flex justify-between items-center">
                        <span class="text-sm font-medium {
                            'text-danger' if '错误' in msg or '失败' in msg else
                            'text-warning' if '警告' in msg or '风险' in msg else
                            'text-success' if '成功' in msg or '完成' in msg else
                            'text-dark'
                        }">
                            <i class="fa {
                                'fa-times-circle' if '错误' in msg or '失败' in msg else
                                'fa-exclamation-triangle' if '警告' in msg or '风险' in msg else
                                'fa-check-circle' if '成功' in msg or '完成' in msg else
                                'fa-circle-o'
                            } mr-1"></i>
                            {msg}
                        </span>
                        <span class="text-xs text-neutral opacity-70">
                            {datetime.now().strftime('%H:%M:%S')}
                        </span>
                    </div>
                </div>
                ''' for msg in log_messages)}
            </div>
        </div>
    </main>

    <!-- 抽屉与遮罩层 -->
    <div id="drawer-overlay" class="drawer-overlay"></div>
    <div id="high-risk-details" class="drawer">
        <span class="drawer-close" onclick="this.parentElement.classList.remove('open'); document.getElementById('drawer-overlay').style.display = 'none';"><i class="fa fa-times"></i></span>
        <div class="p-6">
            <h2 class="section-title flex items-center justify-between">
                <span><i class="fa fa-exclamation-circle text-danger mr-2"></i>高危漏洞详情 ({high_risk}个)</span>
                <span class="text-sm text-neutral">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </h2>
            <div class="space-y-4">
                {''.join(high_risk_details) if high_risk_details else '<p class="text-neutral py-4">未发现高危漏洞</p>'}
            </div>
        </div>
    </div>
    <div id="medium-risk-details" class="drawer">
        <span class="drawer-close" onclick="this.parentElement.classList.remove('open'); document.getElementById('drawer-overlay').style.display = 'none';"><i class="fa fa-times"></i></span>
        <div class="p-6">
            <h2 class="section-title flex items-center justify-between">
                <span><i class="fa fa-exclamation-triangle text-warning mr-2"></i>中危漏洞详情 ({medium_risk}个)</span>
                <span class="text-sm text-neutral">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </h2>
            <div class="space-y-4">
                {''.join(medium_risk_details) if medium_risk_details else '<p class="text-neutral py-4">未发现中危漏洞</p>'}
            </div>
        </div>
    </div>
    <div id="low-risk-details" class="drawer">
        <span class="drawer-close" onclick="this.parentElement.classList.remove('open'); document.getElementById('drawer-overlay').style.display = 'none';"><i class="fa fa-times"></i></span>
        <div class="p-6">
            <h2 class="section-title flex items-center justify-between">
                <span><i class="fa fa-info-circle text-success mr-2"></i>低危漏洞详情 ({low_risk}个)</span>
                <span class="text-sm text-neutral">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </h2>
            <div class="space-y-4">
                {''.join(low_risk_details) if low_risk_details else '<p class="text-neutral py-4">未发现低危漏洞</p>'}
            </div>
        </div>
    </div>

    <!-- 页脚 -->
    <footer class="bg-dark text-white py-6">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <p class="text-sm opacity-80">安全扫描报告 &copy; {datetime.now().year} 北京模湖智能科技有限公司</p>
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
        {js_code}
    </script>
</body>
</html>'''

    # 写入HTML文件
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
    key_message = []

    try:
        if args.poc == 'ray':
            import lib.ray_poc as ray
            if not args.port:
                args.port = 8265
            final = ray.scan_ray(args.ip, args.port)
            
        elif args.poc == 'ollama':
            import lib.ollama_poc as ollama
            if not args.port:
                args.port = 11434
            ollama_scan = ollama.OllamaScanner(args.ip, args.port)
            final = ollama_scan.check_ollama_service()
        elif args.poc == 'llama.cpp':
            import lib.llama_cpp_poc as llama
            if not args.port:
                args.port = 50052
            final = llama.run_llama_poc(args.ip, args.port)
        elif args.poc == 'torchserve':
            import lib.torchserve_poc as torchserve
            if not args.port:
                args.port = 8080
            torchserve_scan = torchserve.TorchServeScanner(args.ip, args.port)
            final = torchserve_scan.check_torchserve_service()
        elif args.poc == 'vllm':
            import lib.vllm_poc as Vllm
            if not args.port:
                args.port = 8989
            port = int(args.port)
            vllm_scan = Vllm.VLLMScanner(args.ip, port)
            final= vllm_scan.check_vllm_service()
        elif args.poc == 'xinference':
            import lib.xinference_poc as xinference
            if not args.port:
                args.port = 35198
            xinference_scan = xinference.XinferenceScanner(args.ip, args.port)
            final= xinference_scan.check_xinference_service()

        elif args.poc == 'all':
            import lib.all_poc as all
            final = all.scan_all_services(args.ip, args.port)
            # banner = final["banner"]
            
        
        if args.poc == 'all':
            args.poc == '全量'
            # print(final)
            results = final["results"]
            cve_tags = final["cve_tags"]
            log_messages = final["log_messages"]
            suggestion = final["suggestions"]
            link = final["links"]
            descriptions = final["descriptions"]
            cvss_scores = final["cvss_scores"]
            key_message = final["key_message"]
        else:
            
            results = final[1]
            cve_tags = final[2]
            log_messages = final[3]
            suggestion = final[4]
            link = final[5]
            descriptions = final[6]
            cvss_scores = final[7]
            key_message = final[8]

        
        # print(log_messages)

        # print(f"正在执行 {args.poc} 模块的安全检测...")
        # print(f"目标 IP 地址: {args.ip}")
        # print(f"目标端口: {args.port}")
        # print(f"启用模块: {banner}")
        # print(f"检测结果: {results}")
        # print(f"检测日志：{log_messages}")

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
        create_html_report(args.ip, args.port, args.poc, results, cve_tags, log_messages, suggestion,cvss_scores , link,descriptions, key_message, args.output)
        print(f"结果已保存到指定文件: {args.output}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
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