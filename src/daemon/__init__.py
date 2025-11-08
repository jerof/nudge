"""
Main daemon loop for monitoring Claude Code output
"""

import time
import logging
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from src.detector import QuestionDetector
from src.notifier import NotificationManager
from src.config import Config

logger = logging.getLogger(__name__)


class ClaudeMonitorDaemon:
    """Monitors log files for Claude Code questions"""

    def __init__(self, config: Config = None):
        """
        Initialize daemon

        Args:
            config: Configuration object (creates default if not provided)
        """
        self.config = config or Config()
        self.detector = QuestionDetector()
        self.notifier = NotificationManager()

        # Track file positions to only read new lines
        self.file_positions: Dict[Path, int] = {}
        self.notification_cooldown = 2  # seconds between notifications
        self.last_notification = None

        self.running = False
        logger.info("Daemon initialized")

    def _should_notify(self) -> bool:
        """Check if enough time has passed since last notification"""
        if self.last_notification is None:
            return True

        elapsed = (datetime.now() - self.last_notification).total_seconds()
        return elapsed >= self.notification_cooldown

    def _process_log_file(self, log_path: Path) -> Optional[str]:
        """
        Check for new lines in log file that indicate a question

        Returns:
            Terminal ID if question detected, None otherwise
        """
        try:
            current_size = log_path.stat().st_size
            last_pos = self.file_positions.get(log_path, 0)

            # File was truncated or reset
            if current_size < last_pos:
                last_pos = 0

            detected_terminal_id = None

            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_pos)

                for line in f:
                    if self.detector.detect(line):
                        # Extract terminal ID from the line
                        terminal_id = self.detector.extract_terminal_id(line)
                        logger.info(f"Question detected in {log_path} from terminal: {terminal_id}")
                        detected_terminal_id = terminal_id

                    # Stop after reading enough lines (efficiency)
                    if self.detector.should_ignore_line(line):
                        continue

                # Update position
                self.file_positions[log_path] = f.tell()

            return detected_terminal_id

        except FileNotFoundError:
            logger.debug(f"Log file not found: {log_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading {log_path}: {e}")
            return None

    def check_logs(self) -> bool:
        """
        Check all monitored log files for questions

        Returns:
            True if question was detected
        """
        log_paths = self.config.get_log_paths()

        if not log_paths:
            if not hasattr(self, '_warned_no_logs'):
                logger.warning("No log paths found. Create ~/.nudge/claude.log or configure paths.")
                self._warned_no_logs = True
            return False

        for log_path in log_paths:
            terminal_id = self._process_log_file(log_path)
            if terminal_id is not None:
                # Question detected, send notification if cooldown allows
                if self._should_notify():
                    if self.notifier.send_notification(terminal_id=terminal_id):
                        self.last_notification = datetime.now()
                        # Try to focus IDE immediately on next iteration
                        time.sleep(0.1)
                        self.notifier.focus_ide(terminal_id=terminal_id)
                    return True

        return False

    def run(self):
        """Main daemon loop"""
        logger.info("Starting daemon loop...")
        self.running = True

        try:
            check_interval = self.config.get("daemon.check_interval", 1)

            while self.running:
                try:
                    self.check_logs()
                    time.sleep(check_interval)

                except KeyboardInterrupt:
                    logger.info("Received interrupt signal")
                    break
                except Exception as e:
                    logger.error(f"Error in daemon loop: {e}")
                    time.sleep(check_interval)

        finally:
            self.stop()

    def stop(self):
        """Stop the daemon"""
        self.running = False
        logger.info("Daemon stopped")


def setup_logging(log_level=logging.INFO):
    """Setup logging for daemon"""
    log_dir = Path.home() / ".nudge"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "nudge.log"

    handlers = [
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    logger.info(f"Logging to {log_file}")


def main():
    """Entry point for daemon"""
    setup_logging()

    config = Config()
    config.ensure_config_dir()

    daemon = ClaudeMonitorDaemon(config)
    daemon.run()


if __name__ == "__main__":
    main()
