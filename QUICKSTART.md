# Nudge - Quick Start Guide

## 🚀 Setup in 5 Minutes

### Step 1: Install Python Dependencies
```bash
cd ~/Desktop/code/nudge
pip install -r requirements.txt
```

### Step 2: Create Log Directory
```bash
mkdir -p ~/.nudge
```

### Step 3: Test the Daemon

**Terminal 1** - Start the daemon:
```bash
python -m src.cli start
```

**Terminal 2** - Simulate a Claude question:
```bash
echo '<invoke name="AskUserQuestion">' >> ~/.nudge/claude.log
```

You should see a notification appear in the top-right corner! 🔔

Click it → Terminal comes to focus.

Press `Ctrl+C` in Terminal 1 to stop the daemon.

---

## 🎯 Run in Background (Auto-start on Login)

```bash
python -m src.cli install
```

That's it! Nudge will now:
- Start automatically when you log in
- Run in the background
- Monitor for Claude questions

---

## 📋 Available Commands

```bash
# Start daemon in foreground (for testing)
python -m src.cli start

# Install as background service (auto-starts on login)
python -m src.cli install

# Check if daemon is running
python -m src.cli status

# View daemon logs
python -m src.cli logs

# Uninstall background service
python -m src.cli uninstall
```

---

## 📝 How to Use with Claude Code

When you run Claude Code and pipe output:

```bash
claude your-task | tee ~/.nudge/claude.log
```

- If Claude asks a question → Nudge sends notification
- Click notification → Terminal comes to focus
- See the question → Respond normally (type 1, 2, 3, etc.)

---

## ✅ Verify Setup

Check if daemon is running:
```bash
python -m src.cli status
```

Should show: `✅ Nudge is running`

---

## 🆘 Troubleshooting

### Notification not appearing?

1. **Check daemon is running:**
   ```bash
   python -m src.cli status
   ```

2. **Check logs:**
   ```bash
   python -m src.cli logs
   ```

3. **Test manually:**
   ```bash
   python -m src.cli start
   # In another terminal:
   echo '<invoke name="AskUserQuestion">' >> ~/.nudge/claude.log
   ```

### Need to uninstall?

```bash
python -m src.cli uninstall
```

---

## 📚 Full Documentation

For detailed setup and configuration, see:
- `README.md` - Project overview
- `INSTALLATION.md` - Detailed setup guide

---

**That's it!** You're ready to use Nudge. 🎉
