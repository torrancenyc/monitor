"""
邮件发送模块 - 使用Resend API
"""
from datetime import datetime
import resend
from config import Config


class EmailSender:
    """邮件发送器 - 使用Resend API"""
    
    def __init__(self):
        self.resend_api_key = Config.RESEND_API_KEY
        self.from_email = Config.FROM_EMAIL
        self.notify_email = Config.NOTIFY_EMAIL
        # 设置 Resend API key
        resend.api_key = self.resend_api_key
    
    def send_notification(self, url, change_info=None):
        """
        发送网站变化通知邮件
        
        Args:
            url: 发生变化的网站URL
            change_info: 变化信息（可选）
        """
        try:
            # 邮件正文
            body = f"""
网站监控系统检测到以下网站发生了变化：

URL: {url}
检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
            if change_info:
                body += f"变化详情:\n{change_info}\n\n"
            
            body += """
"""
            
            # 使用Resend API发送邮件
            params = {
                "from": self.from_email,
                "to": [self.notify_email],
                "subject": f'网站变化通知 - {url}',
                "html": body.replace('\n', '<br>')
            }
            
            resend.Emails.send(params)
            
            print(f"✓ 邮件通知已发送: {url}")
            return True
            
        except Exception as e:
            print(f"✗ 发送邮件失败: {str(e)}")
            return False
    
    def send_error_notification(self, url, error_msg):
        """
        发送错误通知邮件
        
        Args:
            url: 出错的网站URL
            error_msg: 错误信息
        """
        try:
            body = f"""
网站监控系统在检查以下网站时遇到错误：

URL: {url}
错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
错误信息: {error_msg}

请检查网站是否可访问或网络连接是否正常。
"""
            
            params = {
                "from": self.from_email,
                "to": [self.notify_email],
                "subject": f'网站监控错误 - {url}',
                "html": body.replace('\n', '<br>')
            }
            
            resend.Emails.send(params)
            
            print(f"✓ 错误通知邮件已发送: {url}")
            return True
            
        except Exception as e:
            print(f"✗ 发送错误通知邮件失败: {str(e)}")
            return False

