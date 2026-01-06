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

## 🛠 Installation

1.  **Install Python 3.**
2.  **Install Dependencies:**
    ```bash
    pip install rich requests psutil inquirer
    ```
3.  **Install `sshpass` (Mac/Linux only):**
    * **macOS:** `brew install sshpass`
    * **Linux:** `sudo apt install sshpass`

## 🚀 Usage

Run the script:
```bash
python3 main.py
