"""
Question detection logic for Claude Code output
"""

import re
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QuestionDetector:
    """Detects AskUserQuestion tool calls in Claude output"""

    PATTERNS = [
        # Structured JSON patterns
        r'"tool":\s*"AskUserQuestion"',
        r'"name":\s*"AskUserQuestion"',
        r'"subagent_type":\s*"AskUserQuestion"',

        # XML/HTML patterns
        r'<invoke name="AskUserQuestion">',
        r'<invoke.*AskUserQuestion',

        # Text patterns
        r'Questions to ask the user',
    ]

    def extract_terminal_id(self, line: str) -> Optional[str]:
        """
        Extract terminal ID from [TERM:xxx] prefix in log line

        Args:
            line: Log line that may contain [TERM:xxx] prefix

        Returns:
            Terminal ID string if found, None otherwise

        Example:
            >>> detector = QuestionDetector()
            >>> detector.extract_terminal_id("[TERM:term-1762552270-33202-29167] Claude: Should I?")
            'term-1762552270-33202-29167'
            >>> detector.extract_terminal_id("No prefix here")
            None
        """
        if not line:
            return None

        match = re.search(r'\[TERM:([^\]]+)\]', line)
        if match:
            terminal_id = match.group(1)
            logger.debug(f"Extracted terminal ID: {terminal_id}")
            return terminal_id

        return None

    def detect(self, line: str) -> bool:
        """
        Check if a line contains AskUserQuestion indicator or a question

        Returns:
            True if line indicates Claude is asking a question
        """
        if not line or not line.strip():
            return False

        # Strip [TERM:xxx] prefix if present for detection purposes
        # This allows the detector to work with terminal-tagged lines
        cleaned_line = re.sub(r'\[TERM:[^\]]+\]\s*', '', line)

        # Try pattern matching for AskUserQuestion tool
        for pattern in self.PATTERNS:
            if re.search(pattern, cleaned_line, re.IGNORECASE | re.MULTILINE):
                logger.debug(f"Detected pattern: {pattern}")
                return True

        # Try JSON parsing
        try:
            data = json.loads(cleaned_line)
            if isinstance(data, dict):
                if data.get('tool') == 'AskUserQuestion' or \
                   data.get('name') == 'AskUserQuestion' or \
                   'AskUserQuestion' in str(data):
                    logger.debug("Detected via JSON parsing")
                    return True
        except json.JSONDecodeError:
            pass

        # Detect conversational questions (lines ending with ?)
        # Skip short lines and common non-question patterns
        stripped = cleaned_line.strip()
        if stripped.endswith('?') and len(stripped) > 5:
            # Skip lines that are just symbols or formatting
            if not re.match(r'^[>\-\*\s]+\?$', stripped):
                logger.debug(f"Detected conversational question")
                return True

        return False

    def should_ignore_line(self, line: str) -> bool:
        """
        Check if line should be ignored (metadata, etc.)
        """
        ignore_patterns = [
            r'^(DEBUG|INFO|WARNING|ERROR)',  # Log level
            r'^[\s]*$',  # Empty lines
            r'^(sending|received|connection)',  # Connection logs
        ]

        for pattern in ignore_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True

        return False
