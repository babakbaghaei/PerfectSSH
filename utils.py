"""
PerfectSSH - System Utilities
Cross-platform utilities for system operations.
"""

import os
import sys
import shutil
import subprocess
import platform
import requests
import logging
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

class SystemUtils:
    IS_WIN = platform.system() == "Windows"
    IS_MAC = platform.system() == "Darwin"

    @staticmethod
    def clear_screen():
        os.system('cls' if SystemUtils.IS_WIN else 'clear')

    @staticmethod
    def verify_sshpass():
        """Ensures sshpass is installed on non-Windows systems."""
        if SystemUtils.IS_WIN: 
            logger.debug("Windows system detected, skipping sshpass verification")
            return
        
        if not shutil.which("sshpass"):
            logger.warning("sshpass not found, password authentication may not work")
            console.print("[bold yellow]Warning: 'sshpass' not installed. Password authentication may not work.[/bold yellow]\n\nYou can install it with: sudo apt install sshpass")
            # Does not exit anymore

    @staticmethod
    def set_system_proxy(enable=True, port=1080):
        """Configures the system-wide SOCKS5 proxy."""
        logger.info(f"Setting system proxy {'on' if enable else 'off'} on port {port}")
        if SystemUtils.IS_MAC:
            state = "on" if enable else "off"
            # Attempt to set proxy on common network services
            services = ["Wi-Fi", "Ethernet", "Thunderbolt Bridge"]
            for service in services:
                try:
                    # SOCKS Proxy
                    subprocess.run(["networksetup", "-setsocksfirewallproxy", service, "127.0.0.1", str(port)], stderr=subprocess.DEVNULL)
                    subprocess.run(["networksetup", "-setsocksfirewallproxystate", service, state], stderr=subprocess.DEVNULL)
                    # Web Proxy (HTTP/HTTPS) - Optional but good for browsers
                    subprocess.run(["networksetup", "-setwebproxy", service, "127.0.0.1", str(port)], stderr=subprocess.DEVNULL)
                    subprocess.run(["networksetup", "-setwebproxystate", service, state], stderr=subprocess.DEVNULL)
                    subprocess.run(["networksetup", "-setsecurewebproxy", service, "127.0.0.1", str(port)], stderr=subprocess.DEVNULL)
                    subprocess.run(["networksetup", "-setsecurewebproxystate", service, state], stderr=subprocess.DEVNULL)
                except Exception as e:
                    logger.debug(f"Failed to set proxy for {service}: {e}")
                    continue
            logger.info("System proxy configured for macOS")

        elif SystemUtils.IS_WIN:
            import winreg
            try:
                key_path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
                if enable:
                    winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, 'ProxyServer', 0, winreg.REG_SZ, f"socks=127.0.0.1:{port}")
                else:
                    winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
                # Refresh system settings
                os.system('inetcpl.cpl ,4')
                logger.info("System proxy configured for Windows")
            except Exception as e:
                logger.warning(f"Failed to configure Windows proxy: {e}")

        else:
            logger.info("System proxy configuration not supported on this platform")

    @staticmethod
    def kill_existing_ssh():
        """Kills any lingering SSH SOCKS tunnels."""
        logger.debug("Killing existing SSH processes")
        if SystemUtils.IS_WIN:
            os.system("taskkill /F /IM ssh.exe >nul 2>&1")
        else:
            subprocess.run(["pkill", "-f", "ssh.*-D"], stderr=subprocess.DEVNULL)
        logger.info("Existing SSH processes killed")

    @staticmethod
    def fetch_public_ip(proxy_port=None):
        """Fetches the current public IP address."""
        logger.debug(f"Fetching public IP{' via proxy port ' + str(proxy_port) if proxy_port else ''}")
        try:
            proxies = None
            if proxy_port:
                proxies = {
                    'http': f'socks5://127.0.0.1:{proxy_port}',
                    'https': f'socks5://127.0.0.1:{proxy_port}'
                }
            
            response = requests.get('http://ip-api.com/json', proxies=proxies, timeout=8)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Public IP fetched: {data['query']} ({data['countryCode']})")
                return f"[bold green]{data['query']}[/bold green] ({data['countryCode']}, {data['city']})"
        except Exception as e:
            logger.warning(f"Failed to fetch public IP: {e}")
            return "[red]Connection Failed[/red]"
        return "[yellow]Unknown[/yellow]"