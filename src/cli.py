"""
CLI for managing Nudge daemon
"""

import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional

from src.daemon import ClaudeMonitorDaemon, setup_logging
from src.config import Config

logger = logging.getLogger(__name__)

LAUNCHD_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nudge.daemon</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-m</string>
        <string>nudge.daemon</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>{home}/.nudge/nudge.log</string>
    
    <key>StandardErrorPath</key>
    <string>{home}/.nudge/nudge.err</string>
    
    <key>StartInterval</key>
    <integer>5</integer>
</dict>
</plist>
"""


class CLI:
    """Command line interface for Nudge"""
    
    LAUNCHD_LABEL = "com.nudge.daemon"
    LAUNCHD_PATH = Path.home() / "Library/LaunchAgents/com.nudge.daemon.plist"
    
    @staticmethod
    def install():
        """Install daemon as launchd service"""
        logger.info("Installing Nudge as background service...")
        
        # Create config directory
        config = Config()
        config.ensure_config_dir()
        
        # Create launchd plist
        plist_content = LAUNCHD_PLIST.format(
            python_path=sys.executable,
            home=Path.home()
        )
        
        CLI.LAUNCHD_PATH.parent.mkdir(parents=True, exist_ok=True)
        CLI.LAUNCHD_PATH.write_text(plist_content)
        
        logger.info(f"Created {CLI.LAUNCHD_PATH}")
        
        # Load with launchctl
        result = subprocess.run(
            ["launchctl", "load", str(CLI.LAUNCHD_PATH)],
            capture_output=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Nudge installed! It will start on next login.")
            logger.info("   To start now, run: nudge start")
        else:
            logger.error(f"Failed to load launchd agent: {result.stderr.decode()}")
            return False
        
        return True
    
    @staticmethod
    def uninstall():
        """Uninstall daemon"""
        logger.info("Uninstalling Nudge...")
        
        # Unload with launchctl
        subprocess.run(
            ["launchctl", "unload", str(CLI.LAUNCHD_PATH)],
            capture_output=True
        )
        
        # Remove plist
        if CLI.LAUNCHD_PATH.exists():
            CLI.LAUNCHD_PATH.unlink()
            logger.info(f"Removed {CLI.LAUNCHD_PATH}")
        
        logger.info("✅ Nudge uninstalled")
        return True
    
    @staticmethod
    def start():
        """Start daemon (foreground mode for testing)"""
        logger.info("Starting Nudge daemon...")
        
        config = Config()
        daemon = ClaudeMonitorDaemon(config)
        
        try:
            daemon.run()
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
            return True
    
    @staticmethod
    def status():
        """Check if daemon is running"""
        result = subprocess.run(
            ["launchctl", "list", CLI.LAUNCHD_LABEL],
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Nudge is running")
            return True
        else:
            print("❌ Nudge is not running")
            return False
    
    @staticmethod
    def logs():
        """Show daemon logs"""
        log_file = Path.home() / ".nudge/nudge.log"
        
        if not log_file.exists():
            print("No logs found yet")
            return
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Show last 50 lines
                for line in lines[-50:]:
                    print(line, end='')
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")


def main():
    """Main CLI entry point"""
    setup_logging(logging.INFO)
    
    if len(sys.argv) < 2:
        print("Nudge - Claude Code Notification Daemon")
        print()
        print("Usage: nudge <command>")
        print()
        print("Commands:")
        print("  install      Install as background service")
        print("  uninstall    Uninstall background service")
        print("  start        Start daemon (foreground)")
        print("  stop         Stop daemon")
        print("  status       Check daemon status")
        print("  logs         Show daemon logs")
        return
    
    command = sys.argv[1]
    
    if command == "install":
        CLI.install()
    elif command == "uninstall":
        CLI.uninstall()
    elif command == "start":
        CLI.start()
    elif command == "stop":
        # launchctl will handle stopping via unload/load cycle
        print("Use 'nudge uninstall' to stop the daemon")
    elif command == "status":
        CLI.status()
    elif command == "logs":
        CLI.logs()
    else:
        print(f"Unknown command: {command}")
        print("Run 'nudge' for help")


if __name__ == "__main__":
    main()
