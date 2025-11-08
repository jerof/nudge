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
        self.last_terminal_id: Optional[str] = None

    def send_notification(self, terminal_id: Optional[str] = None) -> bool:
        """
        Send notification to macOS notification center (top-right corner)

        Args:
            terminal_id: Terminal identifier for grouping notifications (e.g., term-1762552270-33202-29167).
                        If provided, notifications will be grouped by terminal session.

        Returns:
            True if notification sent successfully
        """
        try:
            # Store terminal_id for later use in focus_ide
            if terminal_id:
                self.last_terminal_id = terminal_id

            # Build notification command with Ghostty activation
            # When user clicks "View", Ghostty will come to focus
            cmd = [
                TERMINAL_NOTIFIER,
                "-title", "Claude Code",
                "-subtitle", "Click to view terminal",
                "-message", "Claude has asked a question",
                "-actions", "View",
                "-sound", "Glass",  # Add sound to make it more noticeable
                "-ignoreDnD",  # Bypass Do Not Disturb
                "-activate", "com.mitchellh.ghostty"  # Activate Ghostty when clicked
            ]

            # Add group flag if terminal_id is provided to group notifications by terminal session
            if terminal_id:
                cmd.extend(["-group", terminal_id])

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5,
                check=False
            )

            if result.returncode == 0:
                logger.info(f"Notification sent successfully (notification center){' for terminal ' + terminal_id if terminal_id else ''}")
                self.notification_sent = True
                return True
            else:
                logger.error(f"Failed to send notification: {result.stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    def focus_ide(self, terminal_id: Optional[str] = None) -> bool:
        """
        Bring IDE/terminal to focus

        Args:
            terminal_id: Terminal identifier for targeting specific terminal window.
                        If provided, can be used for more precise window targeting.

        Returns:
            True if focus command succeeded
        """
        # Store terminal_id for potential future use
        if terminal_id:
            self.last_terminal_id = terminal_id

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
                    logger.info(f"Brought {app} to focus{' (terminal: ' + terminal_id + ')' if terminal_id else ''}")
                    return True
            except Exception as e:
                logger.debug(f"Failed to focus {app}: {e}")
                continue

        logger.error("Could not bring any IDE/terminal to focus")
        return False
