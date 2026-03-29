#!/usr/bin/env python3
"""
Network Device Detector - Phát hiện PC, điện thoại và các thiết bị mạng khác
Discord Style Edition - Fast Version
"""

import socket
import threading
import time
import sys
import os
import subprocess
import platform
from datetime import datetime
from typing import Dict, List
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============= DISCORD STYLE COLOR CODES =============
class Colors:
    DISCORD_BLURPLE = '\033[38;2;114;137;218m'
    DISCORD_GREEN = '\033[38;2;87;242;135m'
    DISCORD_RED = '\033[38;2;237;66;69m'
    DISCORD_YELLOW = '\033[38;2;250;166;26m'
    DISCORD_GREY = '\033[38;2;153;170;181m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_MAGENTA = '\033[1;35m'
    BOLD_WHITE = '\033[1;37m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_GREEN = '\033[1;32m'
    RESET = '\033[0m'

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{Colors.BOLD_CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  {Colors.BOLD_MAGENTA}███╗   ██╗███████╗████████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗{Colors.BOLD_CYAN}    ║
║  {Colors.BOLD_MAGENTA}████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝{Colors.BOLD_CYAN}    ║
║  {Colors.BOLD_MAGENTA}██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ {Colors.BOLD_CYAN}    ║
║  {Colors.BOLD_MAGENTA}██║╚██╗██║██╔══╝     ██║   ██║███╗██║██║   ██║██╔══██╗██╔═██╗ {Colors.BOLD_CYAN}    ║
║  {Colors.BOLD_MAGENTA}██║ ╚████║███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗{Colors.BOLD_CYAN}    ║
║  {Colors.BOLD_MAGENTA}╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝{Colors.BOLD_CYAN}    ║
║                                                                          ║
║     {Colors.BOLD_WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.BOLD_CYAN}     ║
║          {Colors.DISCORD_GREEN}Network Device Detector | Fast Edition{Colors.BOLD_CYAN}                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

def print_menu():
    menu = f"""
{Colors.BOLD_YELLOW}┌─────────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.BOLD_YELLOW}│{Colors.RESET}  {Colors.BOLD_CYAN}[{Colors.DISCORD_GREEN}1{Colors.BOLD_CYAN}]{Colors.RESET} 🔍 Quét mạng một lần                        {Colors.BOLD_YELLOW}│{Colors.RESET}
{Colors.BOLD_YELLOW}│{Colors.RESET}  {Colors.BOLD_CYAN}[{Colors.DISCORD_GREEN}2{Colors.BOLD_CYAN}]{Colors.RESET} 🔄 Quét mạng liên tục                      {Colors.BOLD_YELLOW}│{Colors.RESET}
{Colors.BOLD_YELLOW}│{Colors.RESET}  {Colors.BOLD_CYAN}[{Colors.DISCORD_GREEN}3{Colors.BOLD_CYAN}]{Colors.RESET} 📊 Xem thông tin mạng                      {Colors.BOLD_YELLOW}│{Colors.RESET}
{Colors.BOLD_YELLOW}│{Colors.RESET}  {Colors.BOLD_CYAN}[{Colors.DISCORD_GREEN}4{Colors.BOLD_CYAN}]{Colors.RESET} 💾 Xem lịch sử quét                        {Colors.BOLD_YELLOW}│{Colors.RESET}
{Colors.BOLD_YELLOW}│{Colors.RESET}  {Colors.BOLD_CYAN}[{Colors.DISCORD_RED}0{Colors.BOLD_CYAN}]{Colors.RESET} 🚪 Thoát tool                              {Colors.BOLD_YELLOW}│{Colors.RESET}
{Colors.BOLD_YELLOW}└─────────────────────────────────────────────────────────────┘{Colors.RESET}
"""
    print(menu)

def print_status(status_type, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status_type == "success":
        print(f"{Colors.DISCORD_GREY}[{timestamp}]{Colors.RESET} {Colors.DISCORD_GREEN}[✓]{Colors.RESET} {message}")
    elif status_type == "error":
        print(f"{Colors.DISCORD_GREY}[{timestamp}]{Colors.RESET} {Colors.DISCORD_RED}[✗]{Colors.RESET} {message}")
    elif status_type == "info":
        print(f"{Colors.DISCORD_GREY}[{timestamp}]{Colors.RESET} {Colors.DISCORD_BLURPLE}[ℹ]{Colors.RESET} {message}")
    elif status_type == "warning":
        print(f"{Colors.DISCORD_GREY}[{timestamp}]{Colors.RESET} {Colors.DISCORD_YELLOW}[⚠]{Colors.RESET} {message}")

def classify_device(device):
    hostname = device['hostname'].lower()
    mac = device['mac'].lower()
    
    phones = ['iphone', 'android', 'samsung', 'xiaomi', 'oppo', 'vivo', 'mobile']
    for kw in phones:
        if kw in hostname or kw in mac:
            return "📱 Điện thoại"
    
    computers = ['pc', 'desktop', 'laptop', 'macbook', 'thinkpad', 'dell', 'hp', 'asus']
    for kw in computers:
        if kw in hostname or kw in mac:
            return "💻 Máy tính"
    
    networks = ['router', 'switch', 'gateway', 'modem', 'cisco', 'netgear', 'tp-link']
    for kw in networks:
        if kw in hostname or kw in mac:
            return "🌐 Thiết bị mạng"
    
    return "❓ Thiết bị khác"

class FastNetworkDetector:
    def __init__(self, timeout=0.5, max_workers=50):
        self.timeout = timeout
        self.max_workers = max_workers
        self.devices = []
        self.scan_history = []
        self.network_base = self.get_network_base()
    
    def get_network_base(self):
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'IPv4' in line or 'IP Address' in line:
                        if ':' in line:
                            ip = line.split(':')[1].strip()
                            if ip.startswith(('192.168.', '10.', '172.')):
                                return '.'.join(ip.split('.')[:3])
            else:
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and '127.0.0.1' not in line:
                        ip = line.split()[1].split('/')[0]
                        if ip.startswith(('192.168.', '10.', '172.')):
                            return '.'.join(ip.split('.')[:3])
        except:
            pass
        return None
    
    def get_mac(self, ip):
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        for p in parts:
                            if '-' in p or ':' in p:
                                return p.upper()
            else:
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        if len(parts) > 2:
                            return parts[2].upper()
        except:
            pass
        return "Unknown"
    
    def scan_ip(self, ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            if sock.connect_ex((ip, 80)) == 0:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = "Unknown"
                return {
                    'ip': ip,
                    'hostname': hostname,
                    'mac': self.get_mac(ip),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            sock.close()
        except:
            pass
        return None
    
    def fast_scan(self):
        if not self.network_base:
            print_status("error", "Không tìm thấy mạng!")
            return []
        
        print_status("info", f"Quét {self.network_base}.0/24 với {self.max_workers} luồng...")
        devices = []
        ips = [f"{self.network_base}.{i}" for i in range(1, 255)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.scan_ip, ip): ip for ip in ips}
            
            for i, future in enumerate(as_completed(futures), 1):
                if i % 50 == 0:
                    print(f"\r{Colors.DISCORD_GREY}Đã quét {i}/254 IP...{Colors.RESET}", end="")
                
                result = future.result()
                if result:
                    devices.append(result)
        
        print(f"\r{' ' * 50}\r", end="")
        return devices
    
    def scan_once(self):
        start = time.time()
        self.devices = self.fast_scan()
        elapsed = time.time() - start
        
        self.scan_history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'devices': self.devices.copy()
        })
        
        if self.devices:
            print_status("success", f"Tìm thấy {len(self.devices)} thiết bị trong {elapsed:.1f}s")
            
            # Hiển thị nhanh
            for i, d in enumerate(self.devices[:10], 1):
                dtype = classify_device(d)
                print(f"  {Colors.DISCORD_GREEN}{i}.{Colors.RESET} {dtype} - {d['ip']} - {d['hostname']}")
            
            if len(self.devices) > 10:
                print(f"  {Colors.DISCORD_GREY}... và {len(self.devices)-10} thiết bị khác{Colors.RESET}")
            
            # Lưu file
            self.save_results()
        else:
            print_status("warning", "Không tìm thấy thiết bị nào!")
        
        return self.devices
    
    def continuous_scan(self, interval=10):
        print_status("info", f"Quét liên tục mỗi {interval} giây (Ctrl+C dừng)")
        try:
            while True:
                print(f"\n{Colors.BOLD_CYAN}{'='*50}{Colors.RESET}")
                print_status("info", f"Quét lúc: {datetime.now().strftime('%H:%M:%S')}")
                devices = self.fast_scan()
                print_status("success", f"Tìm thấy {len(devices)} thiết bị")
                
                for d in devices[:5]:
                    dtype = classify_device(d)
                    print(f"  {dtype} - {d['ip']}")
                
                for i in range(interval, 0, -1):
                    print(f"\r{Colors.DISCORD_GREY}Đợi {i}s để quét lại...{Colors.RESET}", end="")
                    time.sleep(1)
                print("\r" + " " * 40 + "\r", end="")
        except KeyboardInterrupt:
            print(f"\n{Colors.DISCORD_YELLOW}Dừng quét{Colors.RESET}")
    
    def save_results(self):
        try:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            txt_file = f"scan_{ts}.txt"
            json_file = f"scan_{ts}.json"
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"Network Scan - {datetime.now()}\n")
                f.write(f"Total: {len(self.devices)} devices\n\n")
                for d in self.devices:
                    f.write(f"{classify_device(d)} | {d['ip']} | {d['hostname']} | {d['mac']}\n")
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=2, ensure_ascii=False)
            
            print_status("success", f"Đã lưu: {txt_file} và {json_file}")
        except Exception as e:
            print_status("error", f"Lỗi lưu: {e}")
    
    def show_history(self):
        if not self.scan_history:
            print_status("warning", "Chưa có lịch sử")
            return
        
        print(f"\n{Colors.BOLD_CYAN}{'='*50}{Colors.RESET}")
        print(f"{Colors.BOLD_WHITE}📜 LỊCH SỬ QUÉT{Colors.RESET}")
        for i, scan in enumerate(self.scan_history[-5:], 1):
            print(f"{Colors.DISCORD_GREEN}{i}.{Colors.RESET} {scan['time']} - {len(scan['devices'])} thiết bị")

def main():
    try:
        if platform.system() != "Windows" and os.geteuid() != 0:
            print(f"{Colors.DISCORD_RED}[!] Cần chạy với sudo!{Colors.RESET}")
            return
        
        detector = FastNetworkDetector(timeout=0.5, max_workers=100)
        
        while True:
            print_banner()
            print_menu()
            
            choice = input(f"\n{Colors.BOLD_WHITE}➤ {Colors.DISCORD_GREEN}").strip()
            
            if choice == "1":
                detector.scan_once()
                input(f"\n{Colors.DISCORD_GREY}Enter để tiếp...{Colors.RESET}")
            
            elif choice == "2":
                interval = input(f"{Colors.DISCORD_GREY}Khoảng cách (giây, mặc định 10): {Colors.DISCORD_GREEN}")
                try:
                    detector.continuous_scan(int(interval) if interval else 10)
                except:
                    detector.continuous_scan(10)
            
            elif choice == "3":
                print(f"\n{Colors.BOLD_GREEN}📡 Mạng: {detector.network_base}.0/24{Colors.RESET}")
                input(f"\n{Colors.DISCORD_GREY}Enter để tiếp...{Colors.RESET}")
            
            elif choice == "4":
                detector.show_history()
                input(f"\n{Colors.DISCORD_GREY}Enter để tiếp...{Colors.RESET}")
            
            elif choice == "0":
                print(f"\n{Colors.DISCORD_YELLOW}👋 Tạm biệt!{Colors.RESET}\n")
                sys.exit(0)
            
            else:
                print_status("error", "Chọn 0-4!")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.DISCORD_YELLOW}👋 Thoát!{Colors.RESET}\n")

if __name__ == "__main__":
    main()
    