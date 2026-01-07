"""
配置文件管理模块
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # Resend API配置
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', '')
    NOTIFY_EMAIL = os.getenv('NOTIFY_EMAIL', '')
    
    # 检查间隔（秒）
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '3600'))
    
    # 文件路径
    URLS_FILE = 'urls.txt'
    STATE_FILE = 'monitor_state.json'
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        if not cls.RESEND_API_KEY:
            raise ValueError("请设置 RESEND_API_KEY 环境变量")
        if not cls.FROM_EMAIL:
            raise ValueError("请设置 FROM_EMAIL 环境变量")
        if not cls.NOTIFY_EMAIL:
            raise ValueError("请设置 NOTIFY_EMAIL 环境变量")
        return True

