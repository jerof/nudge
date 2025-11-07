"""
macOS notification handler using AppleScript
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


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
        Send notification that Claude has asked a question using AppleScript

        Returns:
            True if notification sent successfully
        """
        try:
            # Use AppleScript directly for better compatibility
            script = '''
            display notification "Claude has asked a question" with title "Claude Code"
            '''

            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5,
                check=False
            )

            if result.returncode == 0:
                logger.info("Notification sent successfully")
                self.notification_sent = True
                # Immediately bring IDE to focus when notification is sent
                self.focus_ide()
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
