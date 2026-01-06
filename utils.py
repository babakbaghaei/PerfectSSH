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
        # sshpass is no longer required as we use paramiko exclusively
        logger.debug("sshpass check skipped (not required)")
        return

    @staticmethod
    def _get_macos_active_service():
        """Detects the currently active network service on macOS."""
        try:
            # 1. Get default route interface (e.g., en0)
            result = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True)
            interface_line = [line for line in result.stdout.split('\n') if "interface:" in line]
            if not interface_line:
                return None
            interface = interface_line[0].split(':')[1].strip()

            # 2. Map interface (en0) to Service Name (Wi-Fi)
            result = subprocess.run(["networksetup", "-listallhardwareports"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            current_service = None
            
            for i, line in enumerate(lines):
                if "Hardware Port:" in line:
                    current_service = line.split(':')[1].strip()
                if f"Device: {interface}" in line and current_service:
                    return current_service
                    
        except Exception as e:
            logger.debug(f"Error detecting active service: {e}")
        return None

    @staticmethod
    def set_system_proxy(enable=True, port=1080):
        """Configures the system-wide SOCKS5 proxy."""
        logger.info(f"Setting system proxy {'on' if enable else 'off'} on port {port}")
        if SystemUtils.IS_MAC:
            state = "on" if enable else "off"
            
            # Try to detect active service first
            active_service = SystemUtils._get_macos_active_service()
            services = [active_service] if active_service else ["Wi-Fi", "Ethernet", "Thunderbolt Bridge"]
            
            logger.info(f"Applying proxy settings to: {services}")
            
            for service in services:
                if not service: continue
                try:
                    # SOCKS Proxy
                    subprocess.run(["networksetup", "-setsocksfirewallproxy", service, "127.0.0.1", str(port)], stderr=subprocess.DEVNULL)
                    subprocess.run(["networksetup", "-setsocksfirewallproxystate", service, state], stderr=subprocess.DEVNULL)
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