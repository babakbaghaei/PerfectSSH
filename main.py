#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: PerfectSSH
Description: A minimalist, multi-hop SSH tunnel manager with self-healing capabilities.
Author: Open Source Community
License: MIT
"""

import warnings
# Suppress annoying SSL warnings immediately
warnings.filterwarnings("ignore")

import os
import sys
import signal
import atexit
import time
from datetime import datetime
from pathlib import Path

# --- AUTO-INSTALL DEPENDENCIES ---
def check_dependencies():
    """Checks and installs required Python packages automatically."""
    required_libs = ['rich', 'requests', 'psutil', 'inquirer', 'paramiko']
    missing_libs = []
    
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append(lib)
    
    if missing_libs:
        print(f"Installing missing libraries: {', '.join(missing_libs)}...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_libs)
            print("Libraries installed. Restarting...")
            os.execv(sys.executable, ['python3'] + sys.argv)
        except Exception as e:
            print(f"Critical Error: Could not install dependencies. {e}")
            sys.exit(1)

check_dependencies()

# --- LATE IMPORTS ---
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Confirm

from .utils import SystemUtils
from .config import ConfigManager
from .tunnel import TunnelManager
from .doctor import AutoDoctor
from .ui import get_user_selection, show_dashboard, show_settings
from .logging_config import setup_logging

console = Console()
logger = setup_logging()

# --- GRACEFUL EXIT HANDLER ---
def signal_handler(sig, frame):
    """Handles Ctrl+C to exit cleanly without tracebacks."""
    console.print("\n[yellow]Process interrupted by user. Exiting...[/yellow]")
    # The atexit handler will take care of cleanup
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    logger.info("Starting PerfectSSH")
    SystemUtils.verify_sshpass()
    manager = TunnelManager()
    doctor = AutoDoctor()
    
    # Register cleanup on exit
    atexit.register(manager.disconnect)

    while True:
        SystemUtils.clear_screen()
        console.print(Panel(Align.center("[bold cyan]PERFECTSSH[/bold cyan] [dim]2.0.0[/dim]"), border_style="cyan"))
        
        # --- DASHBOARD STATE ---
        if show_dashboard(manager):
            logger.info("Disconnected from tunnel")
            continue  # Disconnected, continue to menu

        # --- MENU STATE ---
        config = manager.config_manager.config
        is_configured = manager.config_manager.is_configured()
        
        # Dynamic Menu Construction
        menu_choices = []
        if is_configured:
            menu_choices.append(("⚡ Connect", 'conn'))
        
        menu_choices.append(("⚙️ Settings", 'set'))
        
        if is_configured:
            menu_choices.append(("🌍 Check IP", 'ip'))
            menu_choices.append(("🔧 Reset Network", 'tool'))
            
        menu_choices.append(("❌ Exit", 'exit'))
        
        # Display current status summary
        if is_configured:
            mode_display = "Direct" if config['mode'] == '1_hop' else "Bridge"
            console.print(f"Current Profile: [yellow]{mode_display}[/yellow] | Server: [yellow]{config['hop1']['ip']}[/yellow]\n")
        else:
            console.print("[yellow]⚠ No server configured. Please go to Settings.[/yellow]\n")

        selection = get_user_selection("Main Menu", menu_choices)
        
        if not selection or selection == 'exit':
            logger.info("Exiting PerfectSSH")
            manager.disconnect()
            console.print("Goodbye.")
            break

        # --- ACTIONS ---
        if selection == 'conn':
            logger.info("Attempting to establish tunnel connection")
            with console.status("[bold cyan]Establishing Secure Tunnel...[/bold cyan]", spinner="dots"):
                success, msg = manager.connect()
            
            if not success:
                logger.error(f"Connection failed: {msg}")
                console.print(f"[bold red]Connection Failed:[/bold red] {msg}")
                
                # Auto-Doctor Logic
                diagnosis = doctor.analyze_error(msg)
                if diagnosis['fixable']:
                    logger.info(f"Auto-doctor diagnosis: {diagnosis['reason']} (severity: {diagnosis['severity']})")
                    
                    # Display detailed diagnosis
                    console.print(f"\n[bold yellow]🩺 Advanced Diagnosis:[/bold yellow]")
                    console.print(f"Problem: {diagnosis['reason']}")
                    console.print(f"Category: {diagnosis['category'].title()}")
                    console.print(f"Severity: {diagnosis['severity'].title()}")
                    
                    if diagnosis['solutions']:
                        console.print("\n[cyan]Suggested Solutions:[/cyan]")
                        for i, solution in enumerate(diagnosis['solutions'], 1):
                            console.print(f"  {i}. {solution}")
                    
                    if Confirm.ask(f"\n[bold yellow]Attempt comprehensive auto-repair?[/bold yellow]"):
                        # Identify target server
                        target_key = 'hop1'
                        if config['mode'] == '2_hop' and "hop1" not in msg.lower(): 
                            target_key = 'hop2'
                        
                        logger.info(f"Attempting comprehensive auto-repair on {target_key}")
                        with console.status("[bold yellow]🩺 Performing Advanced Surgery on Server...[/bold yellow]", spinner="dots"):
                            repaired, repair_msg = doctor.repair_server(config[target_key])
                        
                        if repaired:
                            logger.info("Server repair successful, retrying connection")
                            console.print("[green]✅ Server Repaired Successfully! Retrying connection...[/green]")
                            time.sleep(2)
                            success, retry_msg = manager.connect()
                            if success:
                                console.print("[green]🎉 Connection established after repair![/green]")
                            else:
                                console.print(f"[yellow]⚠️ Repair completed but connection still failed: {retry_msg}[/yellow]")
                        else:
                            logger.error(f"Server repair failed: {repair_msg}")
                            console.print(f"[red]❌ Repair Failed: {repair_msg}[/red]")
                            console.print("[dim]Manual intervention may be required.[/dim]")
                    else:
                        console.print("[dim]Repair cancelled by user.[/dim]")
                else:
                    console.print(f"[red]❌ Problem not auto-fixable: {diagnosis['reason']}[/red]")
                    if diagnosis['solutions']:
                        console.print("[cyan]Manual solutions:[/cyan]")
                        for solution in diagnosis['solutions']:
                            console.print(f"  • {solution}")
                
                console.input("\nPress Enter to continue...")

        elif selection == 'set':
            show_settings(manager)
            logger.info("Settings updated")

        elif selection == 'ip':
            with console.status("Checking Identity..."):
                ip_info = SystemUtils.fetch_public_ip(config['local_port'] if manager.ssh_client else None)
            console.print(Panel(f"Current IP: {ip_info}", title="Network Status"))
            console.input("Press Enter...")

        elif selection == 'tool':
            SystemUtils.set_system_proxy(False)
            logger.info("System proxy reset")
            console.print("[green]System proxy settings have been reset.[/green]")
            console.input("Press Enter...")

if __name__ == "__main__":
    main()