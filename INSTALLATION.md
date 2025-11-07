# Nudge - Installation & Setup Guide

## Prerequisites

- macOS 10.12+
- Python 3.8+
- Terminal app (Ghostty, iTerm, Terminal) or IDE (VS Code, Cursor)

## Installation

### 1. Clone or Download

```bash
cd ~/Desktop/code
# nudge is already set up here
cd nudge
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with pip in editable mode (for development):

```bash
pip install -e .
```

### 3. Set Up Log Monitoring

The daemon watches for Claude Code questions in log files. Choose one of these approaches:

#### Option A: Create Manual Log File (Recommended for Testing)

```bash
mkdir -p ~/.nudge
touch ~/.nudge/claude.log
```

Then when running Claude Code, pipe output to this file:

```bash
claude your-task | tee ~/.nudge/claude.log
```

#### Option B: Auto-detect Claude Config Directory (if available)

The daemon will automatically watch:
- `~/.config/claude/logs/`
- `~/.claude/logs/`
- `/tmp/claude-code/`

#### Option C: Custom Log Path

Edit `~/.nudge/config.toml` to add your custom log paths:

```toml
[paths]
log_dirs = [
    "~/.nudge/claude.log",
    "~/my/custom/path/claude.log"
]
```

### 4. Install as Background Service

```bash
nudge install
```

This creates a launchd agent that starts Nudge automatically on login.

### 5. Verify Installation

```bash
nudge status
```

Should output: `✅ Nudge is running`

## Usage

### Start Daemon (Testing)

For testing or running in foreground:

```bash
nudge start
```

This will:
- Monitor log files for questions
- Show notifications when questions appear
- Bring IDE/terminal to focus on click

Press `Ctrl+C` to stop.

### Check Status

```bash
nudge status
```

### View Logs

```bash
nudge logs
```

Shows the last 50 lines of daemon activity.

### Uninstall

To remove the background service:

```bash
nudge uninstall
```

## How It Works

1. **You run Claude Code** in your terminal/IDE
2. **Output is logged** to `~/.nudge/claude.log` (or detected location)
3. **Nudge daemon monitors** the log file for `AskUserQuestion` patterns
4. **Notification appears** in macOS notification center when question detected
5. **You click notification** → Terminal/IDE comes to focus
6. **You respond** to the question normally

## Configuration

Edit `~/.nudge/config.toml` to customize:

```toml
[paths]
# Log directories to monitor
log_dirs = [
    "~/.nudge/claude.log",
    "~/.config/claude/logs/",
]

[notification]
# Notification message
title = "Claude Code"
message = "Claude has asked a question"
sound = "default"  # or "none"

[focus]
# Which apps to bring to focus (in order)
terminals = ["Ghostty", "iTerm", "Terminal"]
ides = ["Code", "Cursor"]

[daemon]
# How often to check logs (seconds)
check_interval = 1
```

## Troubleshooting

### Notifications not appearing?

1. **Check if daemon is running:**
   ```bash
   nudge status
   ```

2. **Check logs:**
   ```bash
   nudge logs
   ```

3. **Verify log file exists and contains questions:**
   ```bash
   cat ~/.nudge/claude.log | grep -i AskUserQuestion
   ```

4. **Test detection manually:**
   ```bash
   echo '<invoke name="AskUserQuestion">' > ~/.nudge/test.log
   # Should see "Question detected" in logs after a moment
   nudge logs
   ```

### App not coming to focus?

The daemon tries these apps in order:
- Ghostty, iTerm, Terminal (terminals)
- Code, Cursor (IDEs)

If your IDE/terminal isn't listed, edit `~/.nudge/config.toml`:

```toml
[focus]
terminals = ["YourTerminalName", "Ghostty", "iTerm", "Terminal"]
ides = ["YourIDEName", "Code", "Cursor"]
```

### Daemon won't start?

1. Check that it's not already running:
   ```bash
   launchctl list | grep nudge
   ```

2. If it is, uninstall and reinstall:
   ```bash
   nudge uninstall
   nudge install
   ```

3. Check system logs:
   ```bash
   log show --predicate 'process == "python3"' --last 1h
   ```

## Quick Start Example

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test manually first
nudge start
# In another terminal:
echo 'test line' >> ~/.nudge/claude.log
echo '<invoke name="AskUserQuestion">' >> ~/.nudge/claude.log
# Should see notification appear

# 3. Install as service
nudge install

# 4. Now when you use Claude Code, pipe output:
claude task-name | tee ~/.nudge/claude.log
```

## Uninstallation

To completely remove Nudge:

```bash
nudge uninstall
rm -rf ~/.nudge
pip uninstall nudge-notification
```

## Support

For issues or questions, check:
- README.md for overview
- This file for detailed setup
- `nudge logs` for error details

## Next Steps

- [Phase 2] Add response buttons directly to notifications
- [Phase 2] Question preview in notification
- [Phase 2] Multiple question queue UI
