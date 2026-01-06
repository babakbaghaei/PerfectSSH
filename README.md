# PerfectSSH 🌟

**The Ultimate, Minimalist SSH Tunnel Manager with Auto-Repair.**

PerfectSSH is a lightweight, cross-platform CLI tool designed to establish secure SSH tunnels easily. It features an intuitive **arrow-key menu**, supports **Multi-Hop (Bridge)** connections, and includes an **Auto-Doctor** to fix server-side issues automatically.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20Linux%20%7C%20Win-lightgrey)

## ✨ Features

* **Navigation:** Clean UI with Arrow Key navigation.
* **Modes:**
    * **Direct (1-Hop):** Connect directly to destination.
    * **Bridge (2-Hop):** Relay through an intermediate server (e.g., Iran -> Kharej).
* **🩺 Auto-Doctor:** Automatically diagnoses connection errors and repairs the server (Enables BBR, Fixes SSH Config, Opens Firewall) with one click.
* **📊 Traffic Monitor:** Real-time upload/download stats.
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

## 🩺 Auto-Doctor

The Auto-Doctor can automatically fix common server issues:
- Enable TCP forwarding in SSH config.
- Open firewall ports.
- Enable BBR congestion control.
- Restart SSH service.

## 📊 Traffic Monitoring

Real-time monitoring of:
- Download/Upload speeds.
- Total session data transferred.
- Connection uptime.

## 🐛 Troubleshooting

- **Connection fails:** Check server credentials and network connectivity.
- **sshpass not found:** Install sshpass or use key-based authentication.
- **Permission denied:** Ensure correct username/password or SSH keys.
- **Port issues:** Verify SSH port is open and not blocked by firewall.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful CLI.
- Inspired by various SSH tunneling tools.