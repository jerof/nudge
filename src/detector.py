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
    
    def detect(self, line: str) -> bool:
        """
        Check if a line contains AskUserQuestion indicator
        
        Returns:
            True if line indicates Claude is asking a question
        """
        if not line or not line.strip():
            return False
        
        # Try pattern matching
        for pattern in self.PATTERNS:
            if re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                logger.debug(f"Detected pattern: {pattern}")
                return True
        
        # Try JSON parsing
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                if data.get('tool') == 'AskUserQuestion' or \
                   data.get('name') == 'AskUserQuestion' or \
                   'AskUserQuestion' in str(data):
                    logger.debug("Detected via JSON parsing")
                    return True
        except json.JSONDecodeError:
            pass
        
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
