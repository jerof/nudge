# Nudge Roadmap - Multi-Terminal Support (Phase 2)

**Current Status:** Starting Phase 2 implementation (2025-11-07)

**Goal:** When you have 10 parallel Ghostty terminals running Claude, clicking the notification should bring focus to the SPECIFIC terminal that asked the question, not just any Ghostty window.

---

## The Problem We're Solving

```
Terminal 1: claude task1 (no question)
Terminal 2: claude task2 (no question)
Terminal 3: claude task3 ← ASKS A QUESTION
Terminal 4-10: other tasks

Current behavior: Notification appears → Click "View" → Terminal 7 comes to focus (WRONG!)
Desired behavior: Notification appears → Click "View" → Terminal 3 comes to focus (CORRECT!)
```

---

## Solution Overview

We need to:
1. **Capture** which terminal each Claude output came from
2. **Store** that identity with each question
3. **Use** that identity to switch to the right terminal

### High-Level Flow

```
Before (Current):
  "claude task" → ~/.nudge/claude.log → Daemon detects question → Focus Ghostty (any window)

After (Phase 2):
  "claude task" → ~/.nudge/claude.log WITH TERMINAL_ID → Daemon detects question + extracts ID → Focus Ghostty window with that ID
```

---

## Implementation Steps (In Order!)

### STEP 1: Capture Terminal ID in Shell Wrapper
**File:** `~/.bashrc` and `~/.zshrc`
**What to do:** Add a unique identifier to each log line showing which terminal it came from

**Current code:**
```bash
claude() {
  /Users/nikhilsamuel/.local/bin/claude "$@" | tee ~/.nudge/claude.log
}
```

**After Step 1:**
```bash
claude() {
  TERM_ID="term-$(date +%s%N)"  # Unique ID like: term-1730967123456789000
  /Users/nikhilsamuel/.local/bin/claude "$@" | sed "s/^/[TERM:$TERM_ID] /" | tee ~/.nudge/claude.log
}
```

**Result:** Each line in log will look like:
```
[TERM:term-1730967123456789000] Claude: Should I use React or Vue?
```

**Why:** Regex pattern is simple to extract: `\[TERM:([^\]]+)\]`

---

### STEP 2: Update Detector to Extract Terminal ID
**File:** `src/detector.py`
**What to do:** When we find a question, also extract the terminal ID

**Current code:**
```python
def detect(self, line: str) -> bool:
    if stripped.endswith('?') and len(stripped) > 5:
        return True
```

**After Step 2:**
```python
def detect(self, line: str) -> bool:
    if stripped.endswith('?') and len(stripped) > 5:
        return True

def extract_terminal_id(self, line: str) -> str:
    """Extract [TERM:xyz] from line"""
    match = re.search(r'\[TERM:([^\]]+)\]', line)
    if match:
        return match.group(1)  # "term-1730967123456789000"
    return None
```

**Result:** Detector can now identify questions AND which terminal asked them

---

### STEP 3: Update Daemon to Track Terminal Metadata
**File:** `src/daemon/__init__.py`
**What to do:** When a question is detected, store the terminal ID alongside it

**Current code:**
```python
if detector.detect(line):
    question_found()
    notifier.send_notification()
```

**After Step 3:**
```python
if detector.detect(line):
    terminal_id = detector.extract_terminal_id(line)
    question_found(terminal_id=terminal_id)
    notifier.send_notification(terminal_id=terminal_id)
```

**Result:** Terminal ID gets passed to notifier

---

### STEP 4: Update Notifier to Use Terminal ID
**File:** `src/notifier.py`
**What to do:** When sending notification and when handling click, use the terminal ID

**Current code:**
```python
def send_notification(self) -> bool:
    cmd = [
        TERMINAL_NOTIFIER,
        "-title", "Claude Code",
        "-activate", "com.mitchellh.ghostty"
    ]
```

**After Step 4:**
```python
def send_notification(self, terminal_id: str = None) -> bool:
    cmd = [
        TERMINAL_NOTIFIER,
        "-title", "Claude Code",
        "-activate", "com.mitchellh.ghostty",
        "-group", terminal_id  # Group notifications by terminal ID
    ]

    # Store terminal_id for later focus
    self.last_terminal_id = terminal_id
```

**Then in focus handler:**
```python
def focus_ide(self, terminal_id: str = None) -> bool:
    if terminal_id:
        # Focus the specific Ghostty window that matches this terminal_id
        script = f'tell application "Ghostty" to windows whose name contains "{terminal_id}"'
    # ... rest of activation code
```

**Result:** Notifications linked to specific terminals, notification click knows which terminal to focus

---

### STEP 5: Test with Multiple Terminals
**What to do:** Create 3-5 Ghostty windows and test

**Test steps:**
```bash
# Terminal 1
cd ~/Desktop/code/nudge
echo "[TERM:terminal-1] Claude asks question 1?" >> ~/.nudge/claude.log

# Terminal 2
echo "[TERM:terminal-2] Claude asks question 2?" >> ~/.nudge/claude.log

# Terminal 3
echo "[TERM:terminal-3] Claude asks question 3?" >> ~/.nudge/claude.log

# Click each notification and verify the right window comes to focus
```

**Success criteria:**
- ✅ Each question shows in log with its terminal ID
- ✅ Daemon detects and extracts terminal ID
- ✅ Notification groups by terminal ID
- ✅ Clicking "View" brings the RIGHT terminal to focus (not just any Ghostty window)

---

## Implementation Notes

### Important Design Decisions

**Why use `[TERM:ID]` format?**
- Simple to parse with regex
- Doesn't interfere with Claude's output
- Easy to read in logs for debugging
- Works with pipe/tee mechanism

**Why unique ID instead of terminal name?**
- Terminal names might change or be duplicated
- Unique ID is guaranteed unique per session
- Easier to store in notification metadata

**Why use `-group` in terminal-notifier?**
- macOS groups notifications by app + group ID
- This helps organize notifications from same terminal
- When user clicks, we know which group (terminal) it came from

### Potential Complications

1. **Terminal ID is session-specific** - If terminal closes and reopens, it gets new ID
   - This is OK - old notifications are orphaned (expected behavior)

2. **Ghostty window naming** - We need to verify Ghostty supports window identification by text pattern
   - Fallback: Focus Ghostty app, user manually clicks the right window tab

3. **Multiple terminals in same tab?** - If using tmux/screen inside Ghostty
   - Not supported in Phase 2 (Phase 3 feature)
   - Note this in LIMITATIONS

---

## Files to Modify (Dependency Order)

1. **~/.bashrc** and **~/.zshrc** - Add terminal ID to output (STEP 1)
2. **src/detector.py** - Extract terminal ID from line (STEP 2)
3. **src/daemon/__init__.py** - Pass terminal ID through flow (STEP 3)
4. **src/notifier.py** - Use terminal ID in notification (STEP 4)
5. **Test manually** - Verify with multiple terminals (STEP 5)
6. **Update documentation:**
   - LEARNING.md - Add "Level 11: Terminal ID Implementation"
   - PROGRESS.md - Mark multi-terminal as complete
   - BUGS.md - Note what's still not supported
   - claude.md - Document the terminal ID design

---

## After Implementation: Documentation Updates

Update these files in this order:

### LEARNING.md
Add new section:
```markdown
## Level 11: Implementation - Terminal ID Tracking

[Explain how each step works with quiz questions]
```

### PROGRESS.md
- Mark multi-terminal support as COMPLETE
- Add to "Last Tested" timestamp
- Update Known Limitations
- Add to Success Metrics

### BUGS.md
Add new section:
```markdown
## Phase 2 Multi-Terminal Notes

- Multi-terminal support is now working!
- Limitations:
  - Session-specific IDs (if terminal closes, loses context)
  - Requires Ghostty (other terminals in Phase 3)
  - tmux/screen support pending
```

### claude.md
Add architecture decision:
```markdown
### Terminal ID Tracking (Phase 2)
**Decision:** Use [TERM:unique-id] prefix in log lines
**Rationale:** ...
**Trade-off:** ...
```

---

## Success Criteria for Phase 2

- ✅ Terminal ID captured in every log line
- ✅ Detector extracts terminal ID from questions
- ✅ Daemon passes terminal ID to notifier
- ✅ Notifier groups notifications by terminal ID
- ✅ Clicking "View" focuses the correct terminal (confirmed with manual test)
- ✅ All documentation updated with explanations
- ✅ New LEARNING.md level explaining the implementation
- ✅ Commit all changes with clear messages

---

## Next Steps After Phase 2

Once multi-terminal is working:

1. **Phase 3A: Question Preview**
   - Show actual question text in notification
   - Not just "Claude has asked a question"

2. **Phase 3B: Response Buttons**
   - Add "Yes/No/Other" buttons directly in notification
   - Users respond without opening terminal

3. **Phase 3C: Non-Ghostty Support**
   - Support iTerm, Terminal, VS Code, Cursor
   - Apply terminal ID tracking to all

4. **Phase 4: Dashboard UI**
   - Menu bar app showing all pending questions
   - Click to go to that terminal with question highlighted

---

## How to Use This Roadmap

**For next Claude instance:**
1. Read this entire file
2. Follow STEP 1, 2, 3, 4, 5 in order
3. After each step, update LEARNING.md and PROGRESS.md
4. Commit after each step
5. Test thoroughly before moving to next step

**Current Status:** Ready to start STEP 1 ✅

---

## Quick Reference: What Each File Does

| File | Changes | Step |
|------|---------|------|
| ~/.bashrc | Add terminal ID prefix | 1 |
| ~/.zshrc | Add terminal ID prefix | 1 |
| src/detector.py | Extract terminal ID | 2 |
| src/daemon/__init__.py | Pass terminal ID | 3 |
| src/notifier.py | Use terminal ID in notification | 4 |
| LEARNING.md | Add Level 11 | After 5 |
| PROGRESS.md | Update status | After 5 |
| BUGS.md | Document limitations | After 5 |
| claude.md | Document design decision | After 5 |

---

**Created:** 2025-11-07
**Last Updated:** 2025-11-07
**Owner:** Nudge Team
**Status:** In Planning → Ready for Implementation
