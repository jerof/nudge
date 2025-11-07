# Nudge - Known Issues & Bugs

## 🟢 No Critical Issues

The MVP is stable and tested. This file tracks potential improvements and edge cases.

---

## 🟡 Known Limitations

### 1. Log File Dependency
**Issue:** Nudge relies on Claude Code output being piped to `~/.nudge/claude.log`
- **Impact:** Users must remember to pipe output: `claude task | tee ~/.nudge/claude.log`
- **Solution (Phase 2):** Auto-detect Claude Code log directory or wrap claude command
- **Workaround:** Add alias to .bashrc: `alias claude='claude | tee ~/.nudge/claude.log'`

### 2. Question Text Not in Notification
**Issue:** Notification just says "Claude has asked a question" without showing the actual question
- **Impact:** User must check IDE to see what the question is
- **Solution (Phase 2):** Extract and display question preview in notification
- **Current Behavior:** Intentional for MVP simplicity

### 3. No Response from Notification
**Issue:** Can't answer the question directly from notification
- **Impact:** Must click notification and respond in IDE
- **Solution (Phase 2):** Add native macOS buttons for Yes/No or multiple choice
- **Current Behavior:** Intentional for MVP - keeps scope small

### 4. macOS Only
**Issue:** Only works on macOS
- **Impact:** Not available on Windows or Linux
- **Solution:** Would need platform-specific notification and window management code
- **Scope:** Out of scope for current project (personal tool)

---

## 🟠 Potential Edge Cases (Not Tested)

### 1. Multiple Questions Rapidly
**Scenario:** Claude asks multiple questions in quick succession
- **Current Behavior:** Notification cooldown of 2 seconds prevents spam
- **Potential Issue:** Later questions might be missed if they come within cooldown
- **Fix:** Implement question queue

### 2. Log File Rotation
**Scenario:** Claude log file gets rotated or renamed
- **Current Behavior:** Daemon will log "file not found" but continue monitoring
- **Potential Issue:** Won't detect questions in new log file until restart
- **Fix:** Watch directory instead of just file

### 3. IDE Not in Focus List
**Scenario:** User runs Sublime Text, Vim, or other editor not in default list
- **Current Behavior:** Notification appears but window won't focus
- **Fix:** User can add to `~/.nudge/config.toml`
- **Difficulty:** Low - just need to add app name to config

### 4. Malformed Log Lines
**Scenario:** Log file contains invalid UTF-8 or special characters
- **Current Behavior:** Handled gracefully with `errors='ignore'`
- **Potential Issue:** None identified
- **Status:** ✅ Safe

---

## 🔧 Potential Improvements

### High Priority
- [ ] Auto-detect Claude Code log location instead of manual config
- [ ] Add question text preview to notification
- [ ] Implement question queue for rapid questions

### Medium Priority
- [ ] Better error messages when daemon fails
- [ ] Web UI dashboard for management
- [ ] Support for VS Code/Cursor extensions
- [ ] Custom notification sounds

### Low Priority
- [ ] Cross-platform support (Windows, Linux)
- [ ] Support for other AI tools (not just Claude)
- [ ] Statistics tracking (how many questions, response time, etc.)

---

## 📋 Testing Checklist

Last tested: November 7, 2025

- [x] Daemon starts without errors
- [x] Detects question patterns in log file
- [x] Notification appears in notification center
- [x] Click notification brings Ghostty to focus
- [x] Multiple questions trigger multiple notifications
- [x] Launchd auto-starts on login
- [x] CLI commands work (install, start, status, logs, uninstall)
- [x] Logs are readable and informative
- [ ] Test with VS Code (not yet)
- [ ] Test with Cursor (not yet)
- [ ] Test on clean macOS install

---

## 🐛 Bug Report Template

If you find an issue, please document it:

```
## Title
Brief description

## Steps to Reproduce
1. Step 1
2. Step 2
3. etc.

## Expected Behavior
What should happen

## Actual Behavior
What actually happened

## Logs
Output from `python -m src.cli logs`

## Environment
- macOS version
- Python version
- IDE being used
```

---

## 📞 Help

For issues not listed here:
1. Check `python -m src.cli logs` for errors
2. Review INSTALLATION.md troubleshooting section
3. Verify setup with test: `echo '<invoke name="AskUserQuestion">' >> ~/.nudge/claude.log`
