#!/usr/bin/env python3
"""
YouTube Downloader Tool
Download video and audio from YouTube
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
import json
import re

try:
    import yt_dlp
except ImportError:
    print("[!] yt-dlp not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class YouTubeDownloader:
    def __init__(self, output_path="downloads"):
        self.output_path = output_path
        self.create_output_dir()
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
    def create_output_dir(self):
        """Create output directory if not exists"""
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            print(f"{Colors.GREEN}[+] Created output directory: {self.output_path}{Colors.RESET}")
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"{Colors.RED}[!] Error getting video info: {e}{Colors.RESET}")
            return None
    
    def display_video_info(self, info):
        """Display video information"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}[+] Video Information:{Colors.RESET}")
        print(f"  Title: {Colors.GREEN}{info.get('title', 'N/A')}{Colors.RESET}")
        print(f"  Channel: {Colors.YELLOW}{info.get('uploader', 'N/A')}{Colors.RESET}")
        print(f"  Duration: {self.format_duration(info.get('duration', 0))}")
        print(f"  Views: {info.get('view_count', 0):,}")
        print(f"  Likes: {info.get('like_count', 0):,}")
        print(f"  Upload Date: {info.get('upload_date', 'N/A')}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    def format_duration(self, seconds):
        """Format duration in HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def download_audio(self, url, quality="best"):
        """Download audio only (MP3)"""
        print(f"\n{Colors.BLUE}[+] Downloading audio...{Colors.RESET}")
        
        output_template = os.path.join(self.output_path, '%(title)s.%(ext)s')
        
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': output_template,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')
                print(f"\n{Colors.GREEN}[+] Download complete: {filename}{Colors.RESET}")
                return filename
        except Exception as e:
            print(f"{Colors.RED}[!] Download failed: {e}{Colors.RESET}")
            return None
    
    def download_video(self, url, quality="best", resolution=None):
        """Download video with specific quality"""
        print(f"\n{Colors.BLUE}[+] Downloading video...{Colors.RESET}")
        
        output_template = os.path.join(self.output_path, '%(title)s.%(ext)s')
        
        # Format selection
        if resolution:
            format_spec = f'best[height<={resolution}][ext=mp4]/best[height<={resolution}]/best'
        else:
            format_spec = quality
        
        opts = {
            'format': format_spec,
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'quiet': False,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                print(f"\n{Colors.GREEN}[+] Download complete: {filename}{Colors.RESET}")
                return filename
        except Exception as e:
            print(f"{Colors.RED}[!] Download failed: {e}{Colors.RESET}")
            return None
    
    def download_playlist(self, url, media_type="video", quality="best"):
        """Download entire playlist"""
        print(f"\n{Colors.BLUE}[+] Downloading playlist...{Colors.RESET}")
        
        output_template = os.path.join(self.output_path, '%(playlist)s/%(title)s.%(ext)s')
        
        if media_type == "audio":
            opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'outtmpl': output_template,
                'quiet': False,
                'ignoreerrors': True,
            }
        else:
            opts = {
                'format': f'{quality}[ext=mp4]/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'quiet': False,
                'ignoreerrors': True,
            }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            print(f"\n{Colors.GREEN}[+] Playlist download completed!{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[!] Download failed: {e}{Colors.RESET}")
            return False
    
    def progress_hook(self, d):
        """Display download progress"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    print(f"\r  Progress: {percent:.1f}% | Speed: {speed_mb:.1f} MB/s", end='')
            elif 'total_bytes_estimate' in d:
                percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                print(f"\r  Progress: {percent:.1f}%", end='')
        
        elif d['status'] == 'finished':
            print(f"\r  Processing...", end='')
    
    def search_and_download(self, query, media_type="video", max_results=5):
        """Search YouTube and download first result"""
        print(f"\n{Colors.BLUE}[+] Searching: {query}{Colors.RESET}")
        
        opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    print(f"\n{Colors.CYAN}[+] Search results:{Colors.RESET}")
                    for i, entry in enumerate(info['entries'][:max_results], 1):
                        duration = self.format_duration(entry.get('duration', 0))
                        print(f"  {i}. {Colors.GREEN}{entry.get('title', 'N/A')}{Colors.RESET}")
                        print(f"     Channel: {entry.get('uploader', 'N/A')} | Duration: {duration}")
                    
                    choice = input(f"\n{Colors.YELLOW}[?] Select video number (1-{min(max_results, len(info['entries']))}): {Colors.RESET}")
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(info['entries']):
                            video_url = info['entries'][idx]['webpage_url']
                            if media_type == "audio":
                                return self.download_audio(video_url)
                            else:
                                return self.download_video(video_url)
                        else:
                            print(f"{Colors.RED}[!] Invalid selection{Colors.RESET}")
                    except ValueError:
                        print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[!] Search failed: {e}{Colors.RESET}")
        
        return None

def print_banner():
    """Print program banner"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║   Y O U T U B E   D O W N L O A D E R   T O O L         ║")
    print("║                                                           ║")
    print("║   Download videos and audio from YouTube                 ║")
    print("║   Version 2.0 | Python Edition                           ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def print_menu():
    """Print main menu"""
    print(f"{Colors.YELLOW}")
    print("┌─────────────────────────────────────────────────┐")
    print("│  1. Download Audio (MP3)                        │")
    print("│  2. Download Video (MP4)                        │")
    print("│  3. Download Playlist                           │")
    print("│  4. Search and Download                         │")
    print("│  5. Get Video Information                       │")
    print("│  6. Change Output Directory                     │")
    print("│  0. Exit                                        │")
    print("└─────────────────────────────────────────────────┘")
    print(f"{Colors.RESET}")

def main():
    downloader = YouTubeDownloader()
    
    while True:
        print_banner()
        print_menu()
        
        choice = input(f"{Colors.GREEN}[?] Choose option (0-6): {Colors.RESET}").strip()
        
        if choice == "1":
            url = input(f"{Colors.YELLOW}[?] Enter YouTube URL: {Colors.RESET}").strip()
            if url:
                quality = input(f"{Colors.YELLOW}[?] Audio quality (128/192/320, default 192): {Colors.RESET}").strip()
                quality = quality if quality else "192"
                
                info = downloader.get_video_info(url)
                if info:
                    downloader.display_video_info(info)
                    confirm = input(f"{Colors.YELLOW}[?] Download audio? (y/n): {Colors.RESET}").strip().lower()
                    if confirm == 'y':
                        downloader.download_audio(url, quality)
            
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")
        
        elif choice == "2":
            url = input(f"{Colors.YELLOW}[?] Enter YouTube URL: {Colors.RESET}").strip()
            if url:
                print(f"{Colors.CYAN}[+] Available qualities: 144, 240, 360, 480, 720, 1080, 1440, 2160{Colors.RESET}")
                resolution = input(f"{Colors.YELLOW}[?] Max resolution (default 720): {Colors.RESET}").strip()
                resolution = resolution if resolution else "720"
                
                info = downloader.get_video_info(url)
                if info:
                    downloader.display_video_info(info)
                    confirm = input(f"{Colors.YELLOW}[?] Download video? (y/n): {Colors.RESET}").strip().lower()
                    if confirm == 'y':
                        downloader.download_video(url, resolution=resolution)
            
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")
        
        elif choice == "3":
            url = input(f"{Colors.YELLOW}[?] Enter playlist URL: {Colors.RESET}").strip()
            if url:
                media_type = input(f"{Colors.YELLOW}[?] Download as (video/audio): {Colors.RESET}").strip().lower()
                quality = input(f"{Colors.YELLOW}[?] Quality (default best): {Colors.RESET}").strip()
                quality = quality if quality else "best"
                
                confirm = input(f"{Colors.YELLOW}[?] Download entire playlist? (y/n): {Colors.RESET}").strip().lower()
                if confirm == 'y':
                    downloader.download_playlist(url, media_type, quality)
            
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")
        
        elif choice == "4":
            query = input(f"{Colors.YELLOW}[?] Search query: {Colors.RESET}").strip()
            if query:
                media_type = input(f"{Colors.YELLOW}[?] Download as (video/audio): {Colors.RESET}").strip().lower()
                max_results = input(f"{Colors.YELLOW}[?] Max results (default 5): {Colors.RESET}").strip()
                max_results = int(max_results) if max_results else 5
                
                downloader.search_and_download(query, media_type, max_results)
            
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")
        
        elif choice == "5":
            url = input(f"{Colors.YELLOW}[?] Enter YouTube URL: {Colors.RESET}").strip()
            if url:
                info = downloader.get_video_info(url)
                if info:
                    downloader.display_video_info(info)
                    
                    # Show available formats
                    print(f"\n{Colors.CYAN}[+] Available formats:{Colors.RESET}")
                    formats = info.get('formats', [])
                    seen = set()
                    for f in formats[:20]:
                        if 'height' in f and f['height']:
                            key = f"{f.get('height')}p"
                            if key not in seen:
                                seen.add(key)
                                print(f"  - {key} | Format: {f.get('ext', 'N/A')} | Size: {f.get('filesize', 'N/A')}")
            
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")
        
        elif choice == "6":
            new_path = input(f"{Colors.YELLOW}[?] New output directory (default: downloads): {Colors.RESET}").strip()
            if new_path:
                downloader.output_path = new_path
                downloader.create_output_dir()
                print(f"{Colors.GREEN}[+] Output directory changed to: {new_path}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[!] Using default: downloads{Colors.RESET}")
            
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")
        
        elif choice == "0":
            print(f"\n{Colors.GREEN}[+] Goodbye!{Colors.RESET}")
            sys.exit(0)
        
        else:
            print(f"{Colors.RED}[!] Invalid option!{Colors.RESET}")
            input(f"\n{Colors.CYAN}[*] Press Enter to continue...{Colors.RESET}")

if __name__ == "__main__":
    try:
        # Check for ffmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
        except FileNotFoundError:
            print(f"{Colors.YELLOW}[!] FFmpeg not found. Install ffmpeg for better quality downloads.{Colors.RESET}")
            print(f"{Colors.YELLOW}    - Windows: https://ffmpeg.org/download.html{Colors.RESET}")
            print(f"{Colors.YELLOW}    - Linux: sudo apt install ffmpeg{Colors.RESET}")
            print(f"{Colors.YELLOW}    - Mac: brew install ffmpeg{Colors.RESET}")
        
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
        sys.exit(1)
        