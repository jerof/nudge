# Building in Public: Nudge - Multi-Terminal Claude Notifications

## Twitter Thread (Actionable Focus)

**Thread Start:**

🧵 If you use Claude Code in your terminal, you probably have this problem:

Claude asks you a question. But you're looking at another window. You don't see it. You miss the question entirely.

I built something to fix this. It's called Nudge.

---

**The Problem (You Probably Have This):**

You're running Claude in a terminal tab. Or maybe multiple tabs.

Claude: "Should I use function A or B?"

You: *looking at Slack, email, another code editor*

Result: You miss the question. Claude waits. You waste time searching for which window is asking.

Now multiply this by 10 parallel terminals. Good luck finding the right one.

---

**The Solution:**

Nudge sends you a macOS notification the INSTANT Claude asks a question.

That's it.

✅ Click the notification → your terminal comes to focus
✅ You see the question immediately
✅ You respond and move on

No hunting for windows. No missed questions.

---

**How to Use It (Right Now):**

```bash
# 1. Install
git clone https://github.com/jerof/nudge
cd nudge
pip install -r requirements.txt
python -m src.cli install

# 2. Update your shell (~/.bashrc or ~/.zshrc)
claude() {
  TERM_ID="term-$(date +%s)-$-$RANDOM"
  /path/to/claude "$@" | awk -v id="$TERM_ID" '{print "[TERM:" id "] " $0}' | tee ~/.nudge/claude.log
}

# 3. Done
# Next time Claude asks a question, you'll get a notification
```

That's the setup. It auto-starts on login. Runs invisibly.

---

**The Real Problem I Solved (Multi-Terminal):**

You have 10 Ghostty windows. Claude asks in window #3.

Old behavior: Click notification → terminal 7 comes to focus (WRONG)

New behavior: Click notification → terminal 3 comes to focus (CORRECT)

How?

Each terminal gets a unique ID when you run Claude. That ID travels with the question through the entire system. When you click the notification, it focuses the RIGHT window.

---

**What Changed Under the Hood:**

STEP 1: Shell wrapper tags each line with terminal ID
`[TERM:term-1762552270-33202-29167] Claude: Should I use React?`

STEP 2: Daemon detects question AND extracts the terminal ID

STEP 3: Notification gets grouped by that terminal ID

STEP 4: Clicking notification focuses that specific terminal

Result: Perfect targeting. Multiple terminals work flawlessly.

---

**Real Test Results:**

Added 3 questions from 3 different terminals simultaneously:

```
Terminal 1: "Should I use function A or B?"
Terminal 2: "Is this approach correct?"
Terminal 3: "What's the best practice here?"
```

Result:
✅ All 3 detected correctly
✅ All 3 notifications sent with proper terminal grouping
✅ Clicking each notification focused the correct terminal
```

Works.

---

**What You Get:**

✅ Never miss a Claude question again
✅ Works with multiple parallel terminals
✅ Native macOS notifications (top-right corner)
✅ One-click focus to the right window
✅ Auto-starts on login (runs invisibly)
✅ Fully documented codebase

The entire system is <500 lines of code. Simple. Reliable.

---

**The Tech (If You Care):**

- Python daemon (monitors log files)
- terminal-notifier (macOS native notifications)
- osascript (window management)
- launchd (background service)
- regex pattern matching (question detection)

No external APIs. No cloud. Everything runs locally on your machine.

---

**Why This Matters:**

You're probably losing hours per week missing Claude's questions.

Not because you're lazy. Because you're focused on other things.

Nudge brings Claude's questions to your attention. Immediately. Reliably.

It's a small tool. It solves a real problem. It saves you time every single day.

---

**Next Steps (Try It):**

```bash
# Install
git clone https://github.com/jerof/nudge
cd nudge
pip install -r requirements.txt
python -m src.cli install

# Check status
python -m src.cli status

# Test it
echo "[TERM:test-123] Claude: Should I test this?" >> ~/.nudge/claude.log
# Watch for notification
```

Full docs in README.md

---

**For Power Users:**

Running multiple terminal multiplexers? tmux/screen inside Ghostty?

Nudge still works—it'll focus the app. For precise pane/tab selection, that's Phase 3.

For now: It gets you to the right application. You can find the exact pane.

Future version will handle that too.

---

**The Catch (Be Honest):**

You need to pipe Claude output to a log file:

```bash
claude "your task" | tee ~/.nudge/claude.log
```

Most people already have shell functions for this. Just update it.

It's one line. Takes 30 seconds.

---

**Built in Public:**

- GitHub: https://github.com/jerof/nudge
- Roadmap: See ROADMAP.md for the next features
- Issues: Help wanted on X/tmux support

This is early. But it works. Tested daily.

Contribute, fork, or just use it. All welcome.

---

**One More Thing:**

If you use Claude Code regularly and have multiple terminals, Nudge probably saves you 5+ hours per month.

That's real time. That's real value.

Try it. See if it helps.

If it does, share it.

If it doesn't, tell me why.

Building in public means building with you.

---

GitHub: https://github.com/jerof/nudge
Docs: https://github.com/jerof/nudge/blob/main/README.md

Try it. Tell me what breaks. Let's build this together. 🚀

#BuildingInPublic #Claude #MacOS #DevTools #OpenSource
