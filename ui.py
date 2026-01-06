"""
PerfectSSH - User Interface
Handles the CLI interface using Rich and Inquirer.
"""

import time
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import box
import inquirer

console = Console()
logger = logging.getLogger(__name__)

def get_user_selection(title, choices):
    """Safe wrapper for inquirer to prevent crashes on cancellation."""
    try:
        q = [inquirer.List('opt', message=title, choices=choices)]
        answer = inquirer.prompt(q)
        if not answer: return None
        return answer['opt']
    except KeyboardInterrupt:
        return None

def show_dashboard(manager):
    """Displays the connection dashboard."""
    if manager.ssh_client and manager.ssh_client.get_transport().is_active():
        logger.info("Displaying connection dashboard")
        rx, tx, total = manager.monitor.get_formatted_stats()
        uptime = str(datetime.now() - manager.start_time).split('.')[0]
        
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")
        grid.add_row("[bold green]● CONNECTED[/bold green]", f"Uptime: {uptime}")
        grid.add_row(f"Mode: {manager.config_manager.config['mode']}", f"Port: {manager.config_manager.config['local_port']}")
        
        console.print(Panel(grid, style="green"))
        
        traffic_table = Table(show_header=False, expand=True, box=box.SIMPLE)
        traffic_table.add_row("Download", rx)
        traffic_table.add_row("Upload", tx)
        traffic_table.add_row("Session Total", total)
        
        console.print(Panel(traffic_table, title="Live Traffic", border_style="magenta"))
        console.print(Panel(Align.center("Press [bold red]Ctrl+C[/bold red] to Disconnect"), style="dim"))
        
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            logger.info("User requested disconnection via Ctrl+C")
            manager.disconnect()
            return True  # Disconnected
    return False

def show_settings(manager):
    """Handles the settings menu."""
    logger.info("Entering settings menu")
    while True:
        console.print(Panel("[bold yellow]Configuration Settings[/bold yellow]", border_style="yellow"))
        
        # Mode
        mode_choice = get_user_selection("Select Architecture", [
            ('Direct Connection (1 Server)', '1_hop'),
            ('Bridge Connection (Relay -> Dest)', '2_hop'),
            ('Back', 'back')
        ])
        
        if not mode_choice or mode_choice == 'back': 
            logger.info("Exiting settings menu")
            break
        manager.config_manager.config['mode'] = mode_choice
        logger.info(f"Selected mode: {mode_choice}")
        
        # Server 1 Config
        lbl = "Destination Server" if manager.config_manager.config['mode'] == '1_hop' else "Relay Server (Iran)"
        console.print(f"\n[bold green]┌── {lbl}[/bold green]")
        manager.config_manager.config['hop1']['ip'] = Prompt.ask("│ IP Address", default=manager.config_manager.config['hop1']['ip'])
        manager.config_manager.config['hop1']['port'] = Prompt.ask("│ SSH Port", default=str(manager.config_manager.config['hop1']['port']))
        manager.config_manager.config['hop1']['user'] = Prompt.ask("│ Username", default=manager.config_manager.config['hop1']['user'])
        manager.config_manager.config['hop1']['pass'] = Prompt.ask("│ Password", default=manager.config_manager.config['hop1']['pass'], password=True)
        console.print("[bold green]└──────────────────────────────[/bold green]")
        
        # Server 2 Config (if Bridge)
        if manager.config_manager.config['mode'] == '2_hop':
            console.print(f"\n[bold magenta]┌── Destination Server (Kharej)[/bold magenta]")
            manager.config_manager.config['hop2']['ip'] = Prompt.ask("│ IP Address", default=manager.config_manager.config['hop2']['ip'])
            manager.config_manager.config['hop2']['port'] = Prompt.ask("│ SSH Port", default=str(manager.config_manager.config['hop2']['port']))
            manager.config_manager.config['hop2']['user'] = Prompt.ask("│ Username", default=manager.config_manager.config['hop2']['user'])
            manager.config_manager.config['hop2']['pass'] = Prompt.ask("│ Password", default=manager.config_manager.config['hop2']['pass'], password=True)
            console.print("[bold magenta]└──────────────────────────────[/bold magenta]")
        
        # Local Config
        manager.config_manager.config['local_port'] = int(Prompt.ask("\nLocal SOCKS Port", default=str(manager.config_manager.config['local_port'])))
        manager.config_manager.config['compression'] = Confirm.ask("Enable Compression?", default=manager.config_manager.config['compression'])
        
        manager.config_manager.save()
        logger.info("Settings saved successfully")
        console.print("[bold green]✓ Settings Saved![/bold green]")
        time.sleep(1)
        break