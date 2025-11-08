#!/usr/bin/env python3
"""
Quick test to verify terminal ID extraction works correctly
"""

import sys
sys.path.insert(0, '/Users/nikhilsamuel/Desktop/code/nudge/src')

from detector import QuestionDetector

def test_extract_terminal_id():
    """Test terminal ID extraction"""
    detector = QuestionDetector()

    # Test cases
    test_cases = [
        {
            'line': '[TERM:term-1762552270-33202-29167] Claude: Should I implement step 2 now?',
            'expected_id': 'term-1762552270-33202-29167',
            'expected_detect': True,
            'description': 'Full terminal ID with question'
        },
        {
            'line': '[TERM:term-123-456-789] This is a statement.',
            'expected_id': 'term-123-456-789',
            'expected_detect': False,
            'description': 'Terminal ID without question'
        },
        {
            'line': 'Claude: Should I do this?',
            'expected_id': None,
            'expected_detect': True,
            'description': 'Question without terminal ID'
        },
        {
            'line': 'No terminal ID here',
            'expected_id': None,
            'expected_detect': False,
            'description': 'No terminal ID, no question'
        },
        {
            'line': '[TERM:custom-terminal-abc123] What should I do?',
            'expected_id': 'custom-terminal-abc123',
            'expected_detect': True,
            'description': 'Custom terminal ID with question'
        },
    ]

    print("Testing Terminal ID Extraction and Detection\n")
    print("=" * 70)

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        line = test['line']
        expected_id = test['expected_id']
        expected_detect = test['expected_detect']
        description = test['description']

        # Test extraction
        extracted_id = detector.extract_terminal_id(line)

        # Test detection
        detected = detector.detect(line)

        # Check results
        id_match = extracted_id == expected_id
        detect_match = detected == expected_detect
        passed = id_match and detect_match

        status = "PASS" if passed else "FAIL"

        print(f"\nTest {i}: {description}")
        print(f"  Line: {line}")
        print(f"  Expected ID: {expected_id}")
        print(f"  Extracted ID: {extracted_id} {'✓' if id_match else '✗'}")
        print(f"  Expected Detection: {expected_detect}")
        print(f"  Actual Detection: {detected} {'✓' if detect_match else '✗'}")
        print(f"  Status: {status}")

        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("All tests PASSED!")
        return 0
    else:
        print("Some tests FAILED!")
        return 1

if __name__ == '__main__':
    sys.exit(test_extract_terminal_id())
