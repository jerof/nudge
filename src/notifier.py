"""
macOS notification handler using terminal-notifier for notification center
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)

# Path to terminal-notifier binary
TERMINAL_NOTIFIER = "/opt/homebrew/bin/terminal-notifier"


class NotificationManager:
    """Sends macOS notifications when Claude asks questions"""

    def __init__(self, focus_command: Optional[str] = None):
        """
        Initialize notification manager

        Args:
            focus_command: Command to execute when notification is clicked
        """
        self.focus_command = focus_command
        self.notification_sent = False

    def send_notification(self) -> bool:
        """
        Send notification to macOS notification center (top-right corner)

        Returns:
            True if notification sent successfully
        """
        try:
            # Command to run when notification is clicked - focus the IDE/terminal
            focus_command = 'osascript -e \'tell application "Ghostty" to activate\' 2>/dev/null || osascript -e \'tell application "iTerm" to activate\''

            # Build notification command with improved visibility
            cmd = [
                TERMINAL_NOTIFIER,
                "-title", "Claude Code",
                "-message", "Claude has asked a question",
                "-sound", "Glass",  # Add sound to make it more noticeable
                "-ignoreDnD",  # Bypass Do Not Disturb
                "-execute", focus_command  # Run focus command when clicked
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5,
                check=False
            )

            if result.returncode == 0:
                logger.info("Notification sent successfully (notification center)")
                self.notification_sent = True
                return True
            else:
                logger.error(f"Failed to send notification: {result.stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def focus_ide(self) -> bool:
        """
        Bring IDE/terminal to focus
        
        Returns:
            True if focus command succeeded
        """
        terminals = ["Ghostty", "iTerm", "Terminal"]
        ides = ["Code", "Cursor"]
        app_names = terminals + ides
        
        for app in app_names:
            try:
                script = f'tell application "{app}" to activate'
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    timeout=2,
                    check=False
                )
                
                if result.returncode == 0:
                    logger.info(f"Brought {app} to focus")
                    return True
            except Exception as e:
                logger.debug(f"Failed to focus {app}: {e}")
                continue
        
        logger.error("Could not bring any IDE/terminal to focus")
        return False
