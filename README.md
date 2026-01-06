# PerfectSSH 🌟

**The Ultimate, Minimalist SSH Tunnel Manager with Auto-Repair.**

PerfectSSH is a lightweight, cross-platform CLI tool designed to establish secure SSH tunnels easily. It features an intuitive **arrow-key menu**, supports **Multi-Hop (Bridge)** connections, and includes an **Auto-Doctor** to fix server-side issues automatically.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20%20Linux%20%7C%20Win-lightgrey)

## ✨ Features

* **Navigation:** Clean UI with Arrow Key navigation.
* **Modes:**
    * **Direct (1-Hop):** Connect directly to destination.
    * **Bridge (2-Hop):** Relay through an intermediate server (e.g., Iran -> Kharej).
* **🩺 Advanced Auto-Doctor:** Intelligent diagnosis and comprehensive repair of server issues including SSH configuration, firewall settings, network problems, security fixes, and performance optimization with detailed solution suggestions.
* **📊 Traffic Monitor:** Real-time upload/download stats.
* **🔍 Comprehensive Logging:** Detailed logging with file and console output for debugging and monitoring.
* **🔒 Type Hints:** Full type annotations for better code quality and IDE support.
* **⚡ Retry Logic:** Automatic retry with exponential backoff for connection failures.
* **✅ Configuration Validation:** Built-in validation for server configurations.
* **Cross-Platform:** Works on macOS, Linux, and Windows.
* **Auto-Install Dependencies:** Automatically installs required Python packages.
* **System Proxy Integration:** Automatically configures system proxy settings.

## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/babakbaghaei/PerfectSSH.git
   cd PerfectSSH
   ```

2. **Install Python 3.8+ if not already installed.**

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install `sshpass` (Mac/Linux only, optional but recommended for password auth):**
   * **macOS:** `brew install sshpass`
   * **Linux:** `sudo apt install sshpass`

## 🚀 Usage

Run the script:
```bash
python3 main.py
```

### First Time Setup
1. Run the script.
2. Go to Settings.
3. Choose your connection mode (Direct or Bridge).
4. Enter server details (IP, port, username, password).
5. Save settings.
6. Connect!

### Menu Options
- **⚡ Connect:** Establish the SSH tunnel.
- **⚙️ Settings:** Configure servers and options.
- **🌍 Check IP:** View current public IP (with/without proxy).
- **🔧 Reset Network:** Reset system proxy settings.
- **❌ Exit:** Quit the application.

## 🔧 Configuration

Configuration is stored in `config.json`. You can edit it manually or use the in-app settings.

Example config.json:
```json
{
    "mode": "1_hop",
    "hop1": {
        "ip": "your-server-ip",
        "port": "22",
        "user": "root",
        "pass": "your-password"
    },
    "hop2": {
        "ip": "",
        "port": "22",
        "user": "root",
        "pass": ""
    },
    "local_port": 1080,
    "compression": false
}
```

## 🩺 Advanced Auto-Doctor

The Auto-Doctor is now a comprehensive diagnostic and repair system that can handle virtually all common SSH server issues:

### Diagnostic Capabilities
- **Authentication Issues:** Password problems, SSH key permissions, auth failure limits
- **Connection Problems:** Service down, port blocking, timeouts, network routing
- **Configuration Errors:** TCP forwarding disabled, tunneling issues, SSH settings
- **Security Problems:** Host key verification, permissions, access controls
- **Performance Issues:** Resource limits, network optimization needs
- **Service Problems:** SSH daemon status, startup failures

### Repair Operations
- **Multi-Phase Repair:** Network → SSH Service → Security → Performance → Verification
- **Comprehensive Fixes:**
  - SSH configuration optimization (TcpForwarding, GatewayPorts, KeepAlive, etc.)
  - Firewall management (UFW, iptables, firewalld support)
  - Service management (systemd, sysvinit)
  - Security hardening (permissions, user settings)
  - Performance tuning (BBR, network buffers, system updates)
  - Connectivity verification and testing

### Smart Features
- **Severity Assessment:** High/Medium priority problem classification
- **Solution Suggestions:** Detailed manual fix recommendations
- **Automatic Retry:** Connection re-attempt after successful repair
- **Progress Tracking:** Real-time repair status with detailed logging
- **Verification Phase:** Confirms repairs were successful before declaring victory

## 📊 Traffic Monitoring

Real-time monitoring of:
- Download/Upload speeds.
- Total session data transferred.
- Connection uptime.

## � Logging

PerfectSSH includes comprehensive logging for debugging and monitoring:
- **File Logging:** All logs are saved to `logs/perfectssh.log`
- **Console Logging:** Important messages appear in the terminal
- **Log Levels:** DEBUG, INFO, WARNING, ERROR for different verbosity levels
- **Connection Tracking:** Detailed connection attempts, successes, and failures
- **Auto-Doctor Logs:** Repair operations and their outcomes

## 🐛 Troubleshooting

- **Connection fails:** Check server credentials and network connectivity.
- **sshpass not found:** Install sshpass or use key-based authentication.
- **Permission denied:** Ensure correct username/password or SSH keys.
- **Port issues:** Verify SSH port is open and not blocked by firewall.
- **Check logs:** Review `logs/perfectssh.log` for detailed error information.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful CLI.
- Inspired by various SSH tunneling tools.