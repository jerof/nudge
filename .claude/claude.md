# Claude Code Instructions for Nudge

## Project Overview
Nudge is a macOS daemon that sends notifications when Claude Code asks you a question, and brings your IDE/terminal to focus.

## Tech Stack
- **Language:** Python 3.8+
- **Notifications:** pync (native macOS)
- **Service:** launchd (background daemon)
- **Window Management:** AppleScript/osascript
- **Config:** TOML format
- **Package:** pyproject.toml (modern Python packaging)

## Key Files

### Core Modules
- `src/detector.py` - Detects AskUserQuestion patterns in log files
- `src/notifier.py` - Sends macOS notifications and focuses windows
- `src/config.py` - Configuration management
- `src/daemon/__init__.py` - Main daemon loop
- `src/cli.py` - CLI commands (install/start/status/logs)

### Configuration & Setup
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Package metadata
- `setup.py` - Installation script

### Documentation
- `README.md` - Project overview
- `QUICKSTART.md` - 5-minute setup
- `INSTALLATION.md` - Detailed setup and troubleshooting
- `PROGRESS.md` - Project progress tracking
- `BUGS.md` - Known issues and limitations

## Architecture Decisions

### 1. Log File Monitoring (Not Stdin Capture)
**Decision:** Monitor `~/.nudge/claude.log` instead of wrapping Claude command
**Rationale:**
- Non-invasive: doesn't require modifying how users run Claude
- Reliable: file watching is battle-tested with watchdog/file stats
- Simple: no need for process management or stdin hooks
- User can still see output while it's logged

**Trade-off:** User must pipe output: `claude task | tee ~/.nudge/claude.log`

### 2. Single-Process Daemon (No IPC)
**Decision:** One daemon process handles everything (no worker threads)
**Rationale:**
- Simpler: less to manage, fewer race conditions
- Lighter: single Python process vs. multiple
- Easier debugging: all logs in one place
- Good enough: checking log file every 1 second is responsive

**Trade-off:** Can't distribute work across cores (but not needed for this use case)

### 3. Pattern Matching Detection (Not HTML Parsing)
**Decision:** Use regex patterns to detect `<invoke name="AskUserQuestion">` instead of parsing XML
**Rationale:**
- Fast: regex is instant
- Resilient: works even if format slightly changes
- Simple: no external parser dependencies
- Multiple fallbacks: XML, JSON, text patterns

**Trade-off:** Won't extract question text (Phase 2 feature)

### 4. pync Library (Not pyobjc)
**Decision:** Use pync for notifications instead of pyobjc directly
**Rationale:**
- Simpler API: one function call vs. multiple objc calls
- Better abstraction: handles complexity internally
- Built-in sound support
- Smaller dependency footprint

**Trade-off:** Less control over notification customization (fine for MVP)

### 5. AppleScript for Window Focus (Not Direct APIs)
**Decision:** Use osascript to run AppleScript instead of direct Cocoa APIs
**Rationale:**
- Works across all apps: Terminal, iTerm, VS Code, Cursor, etc.
- Simple: one command line call
- Reliable: AppleScript is stable
- No dependency on app-specific SDKs

**Trade-off:** Slightly slower (subprocess overhead) but not noticeable

### 6. TOML Configuration (Not JSON/YAML)
**Decision:** Use TOML for config instead of JSON or YAML
**Rationale:**
- Human-readable: cleaner syntax than JSON
- Built-in: Python 3.11+ has tomllib
- Less complex than YAML: no indentation gotchas
- Already used by Rust, Python community

**Trade-off:** Requires tomli package for Python < 3.11

### 7. Launchd (Not systemd/cron)
**Decision:** Use launchd for background service on macOS
**Rationale:**
- Native to macOS: no extra daemon framework needed
- Auto-restart: if daemon crashes, launchd restarts it
- Clean logging: can write to files instead of syslog
- Permanent: survives reboots

**Trade-off:** macOS only (intended for personal tool)

## Code Organization

```
src/
├── detector.py       # Core detection logic
├── notifier.py       # Notifications + window focus
├── config.py         # Configuration management
├── daemon/__init__.py # Main event loop
├── cli.py            # Command-line interface
└── __main__.py       # Entry point
```

**Separation of Concerns:**
- Detector: knows how to find questions
- Notifier: knows how to alert user
- Config: knows how to load settings
- Daemon: knows how to run the loop
- CLI: knows how to interact with user

## How It Works

### High Level Flow
```
User runs Claude Code
    ↓
Output piped to ~/.nudge/claude.log
    ↓
Nudge daemon monitors file (checks every 1 second)
    ↓
Detects "<invoke name="AskUserQuestion">"
    ↓
Sends macOS notification via pync
    ↓
User clicks notification
    ↓
osascript activates IDE/terminal
    ↓
User sees question and responds
```

### Detection Process
1. Read new lines from log file (tracks file position)
2. Check each line against patterns
3. When match found, increment match count
4. After cooldown (2 sec), send notification
5. Focus IDE/terminal
6. Return to monitoring

### Key Features
- **File Position Tracking:** Only reads new lines, not whole file
- **Cooldown:** Prevents duplicate notifications for same question
- **Fallback Apps:** Tries multiple apps (Ghostty, iTerm, Terminal, Code, Cursor)
- **Graceful Errors:** Handles missing files, encoding issues, etc.

## Installation Process

### For Users
```bash
pip install -r requirements.txt
python -m src.cli install  # Creates launchd plist
```

### What install does
1. Creates `~/.nudge/` directory
2. Creates `~/.nudge/config.toml` (if not exists)
3. Writes plist to `~/Library/LaunchAgents/com.nudge.daemon.plist`
4. Loads plist with `launchctl load`
5. Daemon auto-starts on next login

## Configuration

Default `~/.nudge/config.toml`:
```toml
[paths]
log_dirs = [
    "~/.nudge/claude.log",
    "~/.config/claude/logs/",
]

[notification]
title = "Claude Code"
message = "Claude has asked a question"
sound = "default"

[focus]
terminals = ["Ghostty", "iTerm", "Terminal"]
ides = ["Code", "Cursor"]

[daemon]
check_interval = 1
```

## Development Workflow

### Running in Foreground
```bash
python -m src.cli start
```
Shows all logs to stdout, easy debugging

### Testing Detection
```bash
echo '<invoke name="AskUserQuestion">' >> ~/.nudge/claude.log
```
Watch logs appear in real-time

### Checking Logs
```bash
python -m src.cli logs  # Last 50 lines
tail -f ~/.nudge/nudge.log  # Live follow
```

### Uninstall
```bash
python -m src.cli uninstall
```
Removes launchd plist and stops daemon

## Performance Considerations

- **CPU:** Minimal - just checking file size + reading new lines
- **Memory:** ~10-20MB - single Python process
- **Disk:** Negligible - log file is text only
- **Battery:** Minimal impact - 1-second check interval is efficient

## Security Considerations

- **Local file only:** Reads from user's home directory
- **No network:** Doesn't send data anywhere
- **No elevated privileges:** Runs as user, not root
- **Notification text:** Doesn't leak question content (by design)

## Future Enhancements (Phase 2)

1. **Response Buttons:** Native macOS buttons for Yes/No, multiple choice
2. **Question Preview:** Show question text in notification
3. **Queue UI:** Dashboard showing pending questions
4. **IDE Extensions:** VS Code/Cursor native integration
5. **Analytics:** Track response times, question frequency

## Debugging Tips

### If notifications not working
1. Check daemon is running: `python -m src.cli status`
2. Check pync installed: `pip list | grep pync`
3. Check config paths: `python -m src.cli logs`
4. Test manually: add line to log, check notification

### If window won't focus
1. Check app name in config matches exactly
2. Check app is installed
3. Test osascript: `osascript -e 'tell application "Ghostty" to activate'`
4. Add custom app to config if different

### If daemon won't start
1. Check logs: `python -m src.cli logs`
2. Check Python version: `python --version` (needs 3.8+)
3. Check dependencies: `pip list`
4. Try foreground: `python -m src.cli start`

## Testing Checklist

- [x] Question detection works
- [x] Notifications appear
- [x] Window focus works
- [x] Launchd auto-starts
- [x] CLI commands functional
- [x] Logs are clear
- [ ] Test on fresh macOS install
- [ ] Test with all IDEs

## Notes

- Project built in one session with Claude Code assistance
- Clean modular architecture ready for Phase 2
- All dependencies pinned in requirements.txt
- Committed to git with clear commit messages
- Deployed to portfolio website (nikhilsamuel.me)
- Ready for public release on GitHub
