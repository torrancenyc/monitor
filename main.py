"""
网站变化监控主程序
"""
import time
import signal
import sys
from monitor import WebsiteMonitor
from config import Config


class MonitorService:
    """监控服务"""
    
    def __init__(self):
        self.monitor = WebsiteMonitor()
        self.running = True
        
        # 注册信号处理，优雅退出
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        print("\n\n收到退出信号，正在停止监控...")
        self.running = False
        sys.exit(0)
    
    def run_once(self):
        """运行一次检查"""
        try:
            self.monitor.monitor_all()
        except Exception as e:
            print(f"监控过程出错: {e}")
    
    def run_continuous(self):
        """持续运行监控"""
        print("=" * 50)
        print("网站变化监控系统启动")
        print("=" * 50)
        print(f"检查间隔: {Config.CHECK_INTERVAL} 秒")
        print(f"监控URL文件: {Config.URLS_FILE}")
        print(f"状态文件: {Config.STATE_FILE}")
        print("=" * 50)
        print("按 Ctrl+C 停止监控\n")
        
        while self.running:
            try:
                self.run_once()
                
                if self.running:
                    print(f"\n等待 {Config.CHECK_INTERVAL} 秒后进行下次检查...")
                    time.sleep(Config.CHECK_INTERVAL)
                    
            except KeyboardInterrupt:
                print("\n\n收到中断信号，正在停止...")
                self.running = False
                break
            except Exception as e:
                print(f"运行出错: {e}")
                if self.running:
                    print(f"等待 {Config.CHECK_INTERVAL} 秒后重试...")
                    time.sleep(Config.CHECK_INTERVAL)


def main():
    """主函数"""
    try:
        # 验证配置
        Config.validate()
        
        # 创建并运行监控服务
        service = MonitorService()
        
        # 检查是否只运行一次
        if len(sys.argv) > 1 and sys.argv[1] == '--once':
            service.run_once()
        else:
            service.run_continuous()
            
    except ValueError as e:
        print(f"配置错误: {e}")
        print("\n请确保已正确配置 .env 文件")
        sys.exit(1)
    except Exception as e:
        print(f"程序出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

