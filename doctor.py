"""
PerfectSSH - Auto Doctor
Diagnoses and repairs server-side SSH issues.
"""

import subprocess
import logging
import time
import paramiko
from utils import SystemUtils

logger = logging.getLogger(__name__)

class AutoDoctor:
    def analyze_error(self, error_msg):
        """Advanced error analysis with comprehensive diagnosis."""
        error = error_msg.lower()
        diagnosis = {
            "reason": "Unknown Error",
            "fixable": False,
            "severity": "unknown",
            "category": "general",
            "solutions": []
        }

        # Authentication Issues
        if "permission denied" in error or "authentication failed" in error:
            diagnosis.update({
                "reason": "Authentication Failed",
                "fixable": True,
                "severity": "high",
                "category": "auth",
                "solutions": ["Check password", "Verify username", "Check SSH key permissions", "Enable password authentication"]
            })
        elif "too many authentication failures" in error:
            diagnosis.update({
                "reason": "Too Many Authentication Failures",
                "fixable": True,
                "severity": "medium",
                "category": "auth",
                "solutions": ["Reduce MaxAuthTries in sshd_config", "Use SSH keys instead of passwords"]
            })

        # Connection Issues
        elif "connection refused" in error:
            diagnosis.update({
                "reason": "SSH Service Not Running or Port Closed",
                "fixable": True,
                "severity": "high",
                "category": "service",
                "solutions": ["Start SSH service", "Open firewall port", "Check SSH port configuration"]
            })
        elif "connection timed out" in error or "timed out" in error:
            diagnosis.update({
                "reason": "Connection Timeout - Network or Firewall Issue",
                "fixable": True,
                "severity": "medium",
                "category": "network",
                "solutions": ["Check network connectivity", "Verify IP address", "Check firewall rules", "Test with different port"]
            })
        elif "no route to host" in error or "network is unreachable" in error:
            diagnosis.update({
                "reason": "Network Routing Issue",
                "fixable": False,
                "severity": "high",
                "category": "network",
                "solutions": ["Check network configuration", "Verify IP reachability", "Contact network administrator"]
            })

        # SSH Configuration Issues
        elif "channel setup failed" in error or "tcp forwarding" in error:
            diagnosis.update({
                "reason": "TCP Forwarding Disabled",
                "fixable": True,
                "severity": "high",
                "category": "config",
                "solutions": ["Enable AllowTcpForwarding", "Enable GatewayPorts", "Restart SSH service"]
            })
        elif "broken pipe" in error or "connection reset by peer" in error:
            diagnosis.update({
                "reason": "Connection Interrupted",
                "fixable": True,
                "severity": "medium",
                "category": "config",
                "solutions": ["Increase ClientAliveInterval", "Check network stability", "Enable KeepAlive"]
            })

        # Host Key Issues
        elif "host key verification failed" in error:
            diagnosis.update({
                "reason": "Host Key Changed or Verification Failed",
                "fixable": True,
                "severity": "medium",
                "category": "security",
                "solutions": ["Remove old host key from known_hosts", "Verify server identity", "Use StrictHostKeyChecking=no for testing"]
            })

        # Resource Issues
        elif "resource temporarily unavailable" in error:
            diagnosis.update({
                "reason": "Server Resource Limits",
                "fixable": True,
                "severity": "medium",
                "category": "system",
                "solutions": ["Check system resources", "Increase limits in limits.conf", "Optimize server performance"]
            })

        logger.info(f"Diagnosed error: {diagnosis['reason']} (severity: {diagnosis['severity']}, fixable: {diagnosis['fixable']})")
        return diagnosis

    def repair_server(self, hop_config):
        """Comprehensive server repair with multiple phases."""
        logger.info(f"Starting comprehensive repair for server {hop_config['ip']}:{hop_config['port']}")

        # Phase 1: Basic connectivity test
        if not self._test_connectivity(hop_config):
            logger.warning("Basic connectivity test failed, attempting network fixes")
            self._repair_network(hop_config)

        # Phase 2: SSH service and configuration
        success, message = self._repair_ssh_service(hop_config)
        if not success:
            logger.error(f"SSH service repair failed: {message}")
            return False, f"SSH Service Repair Failed: {message}"

        # Phase 3: Security and optimization
        self._repair_security(hop_config)
        self._repair_performance(hop_config)

        # Phase 4: Final verification
        if self._verify_repair(hop_config):
            logger.info("Server repair completed successfully")
            return True, "Comprehensive Repair Successful"
        else:
            logger.warning("Repair completed but verification failed")
            return False, "Repair completed but verification failed"

    def _test_connectivity(self, hop_config):
        """Test basic connectivity to server."""
        logger.debug("Testing basic connectivity")
        try:
            # Simple ping test
            result = subprocess.run(['ping', '-c', '2', '-W', '3', hop_config['ip']],
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def _repair_network(self, hop_config):
        """Repair network-related issues."""
        logger.info("Attempting network repairs")
        network_script = r"""
        log() { echo ">>> Network: $1"; }

        log "Checking network interfaces..."
        ip addr show | grep -E "inet |inet6 " | head -5

        log "Testing DNS resolution..."
        nslookup google.com 2>/dev/null || echo "DNS resolution failed"

        log "Checking network routes..."
        ip route show | head -3

        log "Fixing DNS settings..."
        if [ -f /etc/resolv.conf ]; then
            # Backup
            cp /etc/resolv.conf /etc/resolv.conf.backup 2>/dev/null
            # unlocking just in case we locked it before
            chattr -i /etc/resolv.conf 2>/dev/null || true
            
            # Simple overwrite
            echo "nameserver 8.8.8.8" > /etc/resolv.conf
            echo "nameserver 1.1.1.1" >> /etc/resolv.conf
        fi

        log "Network repair complete"
        """
        self._run_remote_script(hop_config, network_script, "network_repair")

    def _repair_ssh_service(self, hop_config):
        """Repair SSH service and configuration."""
        logger.info("Repairing SSH service and configuration")

        ssh_script = r"""
        log() { echo ">>> SSH: $1"; }

        log "Checking SSH service status..."
        if command -v systemctl >/dev/null;
            systemctl is-active sshd >/dev/null 2>&1 || systemctl start sshd
            systemctl enable sshd >/dev/null 2>&1
        elif command -v service >/dev/null;
            service ssh status >/dev/null 2>&1 || service ssh start
        fi

        log "Optimizing SSH configuration..."
        CFG="/etc/ssh/sshd_config"

        # Backup config
        cp "$CFG" "${CFG}.backup.$(date +%s)" 2>/dev/null

        # Essential settings for tunneling
        sed -i 's/^#\?AllowTcpForwarding.*/AllowTcpForwarding yes/g' $CFG
        sed -i 's/^#\?GatewayPorts.*/GatewayPorts yes/g' $CFG
        sed -i 's/^#\?PermitTunnel.*/PermitTunnel yes/g' $CFG
        sed -i 's/^#\?ClientAliveInterval.*/ClientAliveInterval 60/g' $CFG
        sed -i 's/^#\?ClientAliveCountMax.*/ClientAliveCountMax 3/g' $CFG
        sed -i 's/^#\?TCPKeepAlive.*/TCPKeepAlive yes/g' $CFG
        sed -i 's/^#\?MaxAuthTries.*/MaxAuthTries 6/g' $CFG
        sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/g' $CFG
        sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/g' $CFG
        
        # Increase concurrency limits for heavy browsing (images/video)
        sed -i 's/^#\?MaxSessions.*/MaxSessions 1000/g' $CFG
        sed -i 's/^#\?MaxStartups.*/MaxStartups 100:30:1000/g' $CFG

        # Get SSH port
        PORT=$(grep "^Port" $CFG | awk '{print $2}')
        [ -z "$PORT" ] && PORT=22

        log "Opening firewall for SSH port $PORT..."
        if command -v ufw >/dev/null;
            ufw --force enable >/dev/null 2>&1
            ufw allow $PORT/tcp >/dev/null 2>&1
            ufw allow 1080/tcp >/dev/null 2>&1
            ufw reload >/dev/null 2>&1
        fi

        if command -v iptables >/dev/null;
            iptables -I INPUT -p tcp --dport $PORT -j ACCEPT 2>/dev/null
            iptables -I INPUT -p tcp --dport 1080 -j ACCEPT 2>/dev/null
            if command -v iptables-save >/dev/null;
                iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            fi
        fi

        if command -v firewall-cmd >/dev/null;
            firewall-cmd --permanent --add-port=$PORT/tcp >/dev/null 2>&1
            firewall-cmd --permanent --add-port=1080/tcp >/dev/null 2>&1
            firewall-cmd --reload >/dev/null 2>&1
        fi

        log "Restarting SSH service..."
        if command -v systemctl >/dev/null;
            systemctl restart sshd
        elif command -v service >/dev/null;
            service ssh restart
        fi

        log "Waiting for SSH service to stabilize..."
        sleep 3

        log "SSH repair complete"
        echo "SSH_REPAIR_COMPLETE"
        """

        return self._run_remote_script(hop_config, ssh_script, "ssh_repair")

    def _repair_security(self, hop_config):
        """Apply basic security fixes."""
        logger.info("Applying security fixes")

        security_script = r"""
        log() { echo ">>> Security: $1"; }

        log "Checking system users..."
        # Ensure root has proper shell
        usermod -s /bin/bash root 2>/dev/null || true

        log "Setting proper permissions..."
        chmod 600 /etc/ssh/sshd_config 2>/dev/null || true
        chmod 700 /root/.ssh 2>/dev/null || true
        chmod 600 /root/.ssh/* 2>/dev/null || true

        log "Security fixes complete"
        """

        self._run_remote_script(hop_config, security_script, "security_fix")

    def _repair_performance(self, hop_config):
        """Apply performance optimizations."""
        logger.info("Applying performance optimizations")

        perf_script = r"""
        log() { echo ">>> Performance: $1"; }

        log "Enabling BBR congestion control..."
        if ! grep -q "bbr" /etc/sysctl.conf 2>/dev/null;
            echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
            echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
            sysctl -p >/dev/null 2>&1
        fi

        log "Optimizing network buffers..."
        if ! grep -q "net.core.rmem_max" /etc/sysctl.conf 2>/dev/null;
            echo "net.core.rmem_max=16777216" >> /etc/sysctl.conf
            echo "net.core.wmem_max=16777216" >> /etc/sysctl.conf
            echo "net.ipv4.tcp_rmem=4096 87380 16777216" >> /etc/sysctl.conf
            echo "net.ipv4.tcp_wmem=4096 87380 16777216" >> /etc/sysctl.conf
            sysctl -p >/dev/null 2>&1
        fi

        log "Checking system updates..."
        if command -v apt-get >/dev/null; then
            apt-get update >/dev/null 2>&1 && apt-get -y upgrade >/dev/null 2>&1
        elif command -v yum >/dev/null; then
            yum -y update >/dev/null 2>&1
        fi

        log "Increasing system limits..."
        echo "fs.file-max = 65535" >> /etc/sysctl.conf
        echo "net.core.somaxconn = 4096" >> /etc/sysctl.conf
        echo "net.ipv4.ip_local_port_range = 1024 65535" >> /etc/sysctl.conf
        sysctl -p >/dev/null 2>&1
        
        ulimit -n 65535 2>/dev/null || true

        log "Performance optimization complete"
        """

        self._run_remote_script(hop_config, perf_script, "performance_opt")

    def _verify_repair(self, hop_config):
        """Verify that repairs were successful."""
        logger.info("Verifying repair success")

        verify_script = r"""
        log() { echo ">>> Verification: $1"; }

        log "Checking SSH service..."
        if command -v systemctl >/dev/null;
            systemctl is-active sshd >/dev/null 2>&1 && echo "SSH_ACTIVE"
        elif command -v service >/dev/null;
            service ssh status >/dev/null 2>&1 && echo "SSH_ACTIVE"
        fi

        log "Checking SSH configuration..."
        grep -q "AllowTcpForwarding yes" /etc/ssh/sshd_config && echo "TCP_FORWARDING_ENABLED"

        log "Checking firewall..."
        PORT=$(grep "^Port" /etc/ssh/sshd_config | awk '{print $2}')
        [ -z "$PORT" ] && PORT=22

        if command -v ufw >/dev/null;
            ufw status | grep -q "$PORT/tcp" && echo "FIREWALL_OPEN"
        elif command -v iptables >/dev/null;
            iptables -L | grep -q "dpt:$PORT" && echo "FIREWALL_OPEN"
        fi

        log "Verification complete"
        """

        success, output = self._run_remote_script(hop_config, verify_script, "verification")
        if success and "SSH_ACTIVE" in output and "TCP_FORWARDING_ENABLED" in output:
            return True
        return False

    def _run_remote_script(self, hop_config, script, operation_name):
        """Execute a script on the remote server using paramiko."""
        logger.debug(f"Running {operation_name} script on {hop_config['ip']}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=hop_config['ip'],
                port=int(hop_config['port']),
                username=hop_config['user'],
                password=hop_config['pass'],
                timeout=15,
                banner_timeout=30
            )

            logger.debug(f"Executing script via SSH: {operation_name}")
            # Combine lines and escape appropriately if needed, but paramiko exec_command 
            # generally handles the command string as is.
            # The script is a multi-line string, we can execute it by wrapping in bash.
            # However, simpler is often better. The original code replaced newlines with semicolons.
            
            # Using heredoc or passing as argument to bash -s is cleaner for complex scripts
            # But let's stick to the previous logic of joining with semicolons for simplicity if it works,
            # or better, just exec_command(script) if it's valid shell syntax.
            
            # The original code did: full_script = script.replace("\n", " ; ")
            # Let's improve this by executing it as a single bash command.
            
            stdin, stdout, stderr = client.exec_command(f"bash -c {repr(script)}")
            
            # Wait for command to finish
            exit_status = stdout.channel.recv_exit_status()
            
            out_str = stdout.read().decode('utf-8')
            err_str = stderr.read().decode('utf-8')

            if exit_status == 0:
                logger.debug(f"{operation_name} completed successfully")
                return True, out_str
            else:
                logger.warning(f"{operation_name} failed: {err_str}")
                return False, err_str

        except Exception as e:
            logger.error(f"Exception during {operation_name}: {e}")
            return False, str(e)
        finally:
            client.close()