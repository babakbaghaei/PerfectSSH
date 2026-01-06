"""
PerfectSSH - Auto Doctor
Diagnoses and repairs server-side SSH issues.
"""

import subprocess
import logging
from .utils import SystemUtils

logger = logging.getLogger(__name__)

class AutoDoctor:
    def analyze_error(self, error_msg):
        error = error_msg.lower()
        diagnosis = {"reason": "Unknown Error", "fixable": False}

        if "permission denied" in error:
            diagnosis["reason"] = "Authentication Failed (Check Password)"
        elif "connection refused" in error:
            diagnosis["reason"] = "Port Closed or Service Down"
            diagnosis["fixable"] = True
        elif "timed out" in error:
            diagnosis["reason"] = "Connection Timeout (IP might be blocked)"
        elif "channel setup failed" in error:
            diagnosis["reason"] = "Tunneling Disabled (TcpForwarding)"
            diagnosis["fixable"] = True
        
        logger.info(f"Diagnosed error: {diagnosis['reason']} (fixable: {diagnosis['fixable']})")
        return diagnosis

    def repair_server(self, hop_config):
        """Connects to the server and runs a repair script."""
        logger.info(f"Attempting to repair server {hop_config['ip']}:{hop_config['port']}")
        
        # Bash script to optimize server settings
        repair_script = r"""
        log() { echo ">>> $1"; }
        
        log "Optimizing SSH Config..."
        CFG="/etc/ssh/sshd_config"
        sed -i 's/^#\?AllowTcpForwarding.*/AllowTcpForwarding yes/g' $CFG
        sed -i 's/^#\?GatewayPorts.*/GatewayPorts yes/g' $CFG
        sed -i 's/^#\?ClientAliveInterval.*/ClientAliveInterval 60/g' $CFG
        
        log "Opening Firewall..."
        PORT=$(grep "^Port" $CFG | awk '{print $2}')
        [ -z "$PORT" ] && PORT=22
        
        if command -v ufw >/dev/null; then ufw allow $PORT/tcp; ufw allow 1080/tcp; ufw reload; fi
        if command -v iptables >/dev/null; then 
            iptables -I INPUT -p tcp --dport $PORT -j ACCEPT
            iptables -I INPUT -p tcp --dport 1080 -j ACCEPT
        fi
        
        log "Enabling BBR..."
        if ! grep -q "bbr" /etc/sysctl.conf; then
            echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
            echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
            sysctl -p
        fi
        
        log "Restarting SSH Service..."
        if command -v systemctl >/dev/null; then systemctl restart sshd; else service ssh restart; fi
        
        echo "REPAIR_COMPLETE"
        """
        repair_script = repair_script.replace("\n", " ; ")
        
        # Build Command
        cmd = ['ssh']
        if not SystemUtils.IS_WIN:
            cmd = ['sshpass', '-p', hop_config['pass']] + cmd
            
        cmd += [
            '-p', str(hop_config['port']),
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            f"{hop_config['user']}@{hop_config['ip']}",
            'bash -s'
        ]
        
        try:
            logger.debug(f"Running repair command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=repair_script)
            
            if "REPAIR_COMPLETE" in stdout:
                logger.info("Server repair completed successfully")
                return True, "Optimization Successful"
            else:
                logger.error(f"Server repair failed: {stderr.strip()}")
                return False, stderr.strip()
        except Exception as e:
            logger.error(f"Exception during server repair: {e}")
            return False, str(e)