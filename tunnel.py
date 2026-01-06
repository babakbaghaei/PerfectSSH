"""
PerfectSSH - Tunnel Manager
Manages SSH tunnel connections using paramiko.
"""

import threading
import time
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import paramiko
import logging
from utils import SystemUtils
from config import ConfigManager
from proxy import SocksProxy

logger = logging.getLogger(__name__)

class TrafficMonitor:
    def __init__(self):
        self.active: bool = False
        self.rx_speed: int = 0
        self.tx_speed: int = 0
        self.total_data: int = 0
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self.active = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.active = False

    def _monitor_loop(self) -> None:
        import psutil
        last_io = psutil.net_io_counters()
        while self.active:
            time.sleep(1)
            try:
                curr_io = psutil.net_io_counters()
                self.rx_speed = curr_io.bytes_recv - last_io.bytes_recv
                self.tx_speed = curr_io.bytes_sent - last_io.bytes_sent
                self.total_data += (self.rx_speed + self.tx_speed)
                last_io = curr_io
            except:
                pass

    def get_formatted_stats(self) -> Tuple[str, str, str]:
        def human_fmt(num: int) -> str:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if abs(num) < 1024.0:
                    return f"{num:3.1f} {unit}"
                num /= 1024.0
            return f"{num:.1f} TB"
        
        return (
            f"[green]⬇ {human_fmt(self.rx_speed)}/s[/green]",
            f"[blue]⬆ {human_fmt(self.tx_speed)}/s[/blue]",
            f"[white]{human_fmt(self.total_data)}[/white]"
        )

class TunnelManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.relay_client: Optional[paramiko.SSHClient] = None
        self.socks_proxy: Optional[SocksProxy] = None
        self.monitor = TrafficMonitor()
        self.start_time: Optional[datetime] = None
        self.max_retries: int = 3
        self.retry_delay: int = 2

    def connect(self) -> Tuple[bool, str]:
        cfg = self.config_manager.config
        logger.info(f"Attempting to connect in {cfg['mode']} mode")
        SystemUtils.kill_existing_ssh()
        
        for attempt in range(self.max_retries):
            try:
                if cfg['mode'] == '1_hop':
                    logger.debug("Connecting in direct mode")
                    return self._connect_direct(cfg)
                else:
                    logger.debug("Connecting in bridge mode")
                    return self._connect_bridge(cfg)
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All connection attempts failed: {e}")
                    return False, str(e)
                time.sleep(self.retry_delay)

    def _connect_direct(self, cfg: Dict[str, Any]) -> Tuple[bool, str]:
        hop1 = cfg['hop1']
        if not hop1['ip']:
            logger.error("Server IP is missing for direct connection")
            return False, "Server IP is missing."
        
        logger.info(f"Connecting to {hop1['ip']}:{hop1['port']} as {hop1['user']}")
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh_client.connect(
                hostname=hop1['ip'],
                port=int(hop1['port']),
                username=hop1['user'],
                password=hop1['pass'],
                timeout=10
            )
            
            # Start SOCKS proxy
            transport = self.ssh_client.get_transport()
            self.socks_proxy = SocksProxy(cfg['local_port'], transport)
            self.socks_proxy.start()
            
            self.start_time = datetime.now()
            self.monitor.start()
            SystemUtils.set_system_proxy(True, cfg['local_port'])
            logger.info(f"Direct connection established successfully on port {cfg['local_port']}")
            return True, "Connected"
            
        except paramiko.AuthenticationException:
            logger.error("Authentication failed for direct connection")
            return False, "Authentication failed"
        except paramiko.SSHException as e:
            logger.error(f"SSH error in direct connection: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error in direct connection: {e}")
            return False, str(e)

    def _connect_bridge(self, cfg: Dict[str, Any]) -> Tuple[bool, str]:
        hop1 = cfg['hop1']  # Relay
        hop2 = cfg['hop2']  # Destination
        if not hop1['ip'] or not hop2['ip']:
            logger.error("Server IPs are missing for bridge connection")
            return False, "Server IPs are missing."
        
        logger.info(f"Connecting to relay {hop1['ip']}:{hop1['port']} as {hop1['user']}")
        # Connect to relay first
        self.relay_client = paramiko.SSHClient()
        self.relay_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.relay_client.connect(
                hostname=hop1['ip'],
                port=int(hop1['port']),
                username=hop1['user'],
                password=hop1['pass'],
                timeout=10
            )
            
            logger.info(f"Relay connected, now connecting to destination {hop2['ip']}:{hop2['port']} as {hop2['user']}")
            # Use relay as proxy for destination
            sock = self.relay_client.get_transport().open_channel(
                'direct-tcpip', (hop2['ip'], int(hop2['port'])), ('', 0)
            )
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=hop2['ip'],
                port=int(hop2['port']),
                username=hop2['user'],
                password=hop2['pass'],
                sock=sock,
                timeout=10
            )
            
            # Start SOCKS proxy
            transport = self.ssh_client.get_transport()
            self.socks_proxy = SocksProxy(cfg['local_port'], transport)
            self.socks_proxy.start()
            
            self.start_time = datetime.now()
            self.monitor.start()
            SystemUtils.set_system_proxy(True, cfg['local_port'])
            logger.info(f"Bridge connection established successfully on port {cfg['local_port']}")
            return True, "Connected"
            
        except paramiko.AuthenticationException:
            logger.error("Authentication failed for bridge connection")
            if self.relay_client:
                self.relay_client.close()
            return False, "Authentication failed"
        except paramiko.SSHException as e:
            logger.error(f"SSH error in bridge connection: {e}")
            if self.relay_client:
                self.relay_client.close()
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error in bridge connection: {e}")
            if self.relay_client:
                self.relay_client.close()
            return False, str(e)

    def disconnect(self) -> None:
        logger.info("Disconnecting tunnel")
        if self.socks_proxy:
            self.socks_proxy.stop()
            self.socks_proxy = None
            logger.debug("SOCKS proxy stopped")
        if self.ssh_client:
            self.ssh_client.close()
            logger.debug("SSH client closed")
        if self.relay_client:
            self.relay_client.close()
            logger.debug("Relay client closed")
        self.monitor.stop()
        SystemUtils.set_system_proxy(False)
        SystemUtils.kill_existing_ssh()
        logger.info("Tunnel disconnected successfully")