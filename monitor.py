"""
网站监控核心模块
"""
import hashlib
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from email_sender import EmailSender
from config import Config


class WebsiteMonitor:
    """网站监控器"""
    
    def __init__(self):
        self.state_file = Config.STATE_FILE
        self.email_sender = EmailSender()
        self.state = self.load_state()
    
    def load_state(self):
        """加载之前保存的监控状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载状态文件失败: {e}")
                return {}
        return {}
    
    def save_state(self):
        """保存当前监控状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态文件失败: {e}")
    
    def fetch_url_content(self, url):
        """
        获取URL的内容
        
        Args:
            url: 要获取的URL
            
        Returns:
            tuple: (成功标志, 内容或错误信息)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML，提取文本内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本内容
            text = soup.get_text()
            
            # 清理空白字符
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return True, text
            
        except requests.exceptions.RequestException as e:
            return False, f"请求错误: {str(e)}"
        except Exception as e:
            return False, f"处理错误: {str(e)}"
    
    def calculate_hash(self, content):
        """
        计算内容的哈希值
        
        Args:
            content: 要计算哈希的内容
            
        Returns:
            str: 内容的MD5哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def check_url(self, url):
        """
        检查单个URL是否有变化
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 是否有变化
        """
        print(f"\n检查 URL: {url}")
        
        # 获取当前内容
        success, content = self.fetch_url_content(url)
        
        if not success:
            print(f"✗ 获取内容失败: {content}")
            # 可选：发送错误通知
            # self.email_sender.send_error_notification(url, content)
            return False
        
        # 计算当前内容的哈希值
        current_hash = self.calculate_hash(content)
        
        # 检查是否有之前保存的状态
        if url in self.state:
            previous_hash = self.state[url].get('hash', '')
            last_check = self.state[url].get('last_check', '')
            
            if previous_hash and current_hash != previous_hash:
                # 检测到变化
                print(f"✓ 检测到变化！")
                print(f"  上次检查: {last_check}")
                print(f"  上次哈希: {previous_hash[:16]}...")
                print(f"  当前哈希: {current_hash[:16]}...")
                
                # 发送通知邮件
                change_info = f"内容哈希值已从 {previous_hash[:16]}... 变为 {current_hash[:16]}..."
                self.email_sender.send_notification(url, change_info)
                
                # 更新状态
                self.state[url] = {
                    'hash': current_hash,
                    'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'last_change': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.save_state()
                return True
            else:
                # 没有变化
                print(f"✓ 无变化")
                # 更新最后检查时间
                self.state[url]['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_state()
                return False
        else:
            # 首次检查，保存初始状态
            print(f"✓ 首次检查，保存初始状态")
            self.state[url] = {
                'hash': current_hash,
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'first_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.save_state()
            return False
    
    def load_urls(self):
        """
        从文件加载URL列表
        
        Returns:
            list: URL列表
        """
        urls = []
        if os.path.exists(Config.URLS_FILE):
            try:
                with open(Config.URLS_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        url = line.strip()
                        if url and not url.startswith('#'):  # 忽略空行和注释
                            urls.append(url)
            except Exception as e:
                print(f"读取URL文件失败: {e}")
        else:
            print(f"警告: {Config.URLS_FILE} 文件不存在")
        return urls
    
    def monitor_all(self):
        """监控所有URL"""
        urls = self.load_urls()
        
        if not urls:
            print("没有要监控的URL")
            return
        
        print(f"\n开始监控 {len(urls)} 个URL...")
        print("=" * 50)
        
        for url in urls:
            try:
                self.check_url(url)
            except Exception as e:
                print(f"✗ 检查 {url} 时出错: {e}")
        
        print("\n" + "=" * 50)
        print("检查完成")

