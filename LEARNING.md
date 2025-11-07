# Nudge Learning Guide: Understanding the Project Step-by-Step

Welcome! This guide will help you understand how Nudge works, from the simplest concepts to deep technical details. We'll use a Socratic approach: explaining concepts, then asking quiz questions before moving to the next level.

**How to use this guide:**
1. Read each section carefully
2. Try to answer the quiz question before looking at the answer
3. If you get it right, move to the next section
4. If you're unsure, re-read that section
5. No rush - pause and restart whenever you want!

---

## Level 1: The Big Picture (30 seconds)

### What is Nudge?

**Nudge is a helper that watches for Claude to ask you a question, and tells you about it.**

Imagine you're writing code with Claude in your terminal, and Claude asks "Should I use function A or B?" But you don't see the question because you're looking at another window. **Nudge sends you a notification** so you don't miss it.

That's it! Simple, right?

---

### Quiz 1: The Purpose
**Question:** If you have 10 Ghostty terminal windows open running Claude, why would you need Nudge?

<details>
<summary>Click to see answer</summary>

**Answer:** Because Claude might ask a question in window #3, but you're looking at window #7. Without Nudge, you'd miss the question in window #3 and waste time. Nudge tells you "Hey, window #3 needs you!"

</details>

---

## Level 2: How It Works (The 60-Second Version)

### The Simple Flow

```
You run: claude "write a function"
    ↓
Output goes to a file: ~/.nudge/claude.log
    ↓
Nudge daemon reads that file every 1 second
    ↓
Nudge sees "Claude has asked a question?"
    ↓
Nudge sends you a notification (ding!)
    ↓
You click the notification
    ↓
Your terminal comes to the front
    ↓
You see the question and answer it
```

**That's the whole thing!**

---

### Quiz 2: The Flow
**Question:** Why does Nudge check the file every 1 second instead of constantly (like every 10 milliseconds)?

<details>
<summary>Click to see answer</summary>

**Answer:** Because checking every 10 milliseconds would waste CPU and battery. Checking every 1 second is fast enough - you won't notice the 1-second delay when Claude asks a question. It's a good balance between responsiveness and efficiency.

</details>

---

## Level 3: The Components (How It's Built)

### Four Main Parts

Nudge has 4 main pieces that work together:

#### 1. **The Detective** (detector.py)
- Job: Read the log file and find questions
- Question it answers: "Did Claude ask something?"
- How: Uses patterns/regex to look for "?" or "AskUserQuestion"

#### 2. **The Messenger** (notifier.py)
- Job: Send notifications and bring your terminal to focus
- Question it answers: "How do I tell the user?"
- How: Uses terminal-notifier to send Mac notifications, osascript to focus apps

#### 3. **The Brain** (daemon/__init__.py)
- Job: Keep the whole thing running and coordinate everything
- Question it answers: "What should happen next?"
- How: Runs in a loop: check → detect → notify → wait → repeat

#### 4. **The Interface** (cli.py)
- Job: Let you control Nudge from your terminal
- Question it answers: "How does the user tell Nudge what to do?"
- How: Provides commands like `nudge start`, `nudge status`, `nudge logs`

---

### Quiz 3: Components
**Question:** Which part is responsible for actually sending the notification sound and popup?

<details>
<summary>Click to see answer</summary>

**Answer:** The **Messenger** (notifier.py). It's the one that calls terminal-notifier to create the Mac notification with sound.

</details>

---

## Level 4: The Data Flow (Connecting the Pieces)

### Step-by-Step Data Journey

```
1. You type: claude "help me code"
   ↓
2. Output is piped to: ~/.nudge/claude.log
   (thanks to the shell wrapper function)
   ↓
3. Daemon Brain loops every 1 second and reads the log
   ↓
4. Detective looks at each new line and asks: "Is this a question?"
   - Looks for: lines ending with "?"
   - Looks for: "<invoke name="AskUserQuestion">"
   ↓
5. If Detective finds a question → triggers Messenger
   ↓
6. Messenger calls:
   - terminal-notifier (send sound + popup)
   - osascript (bring Ghostty to front)
   ↓
7. You see notification, click "View"
   ↓
8. Ghostty window comes to focus
```

---

### Quiz 4: Data Flow
**Question:** If you run `claude task | tee ~/.nudge/claude.log`, what does the `tee` command do?

<details>
<summary>Click to see answer</summary>

**Answer:** `tee` does two things at once:
1. Shows the output in your terminal (so you see it)
2. Saves it to the file ~/.nudge/claude.log (so Nudge can read it)

Without `tee`, Nudge wouldn't see the output!

</details>

---

## Level 5: The Code Structure (Technical Deep Dive)

### File Organization

```
nudge/
├── src/
│   ├── detector.py       # Regex patterns to find questions
│   ├── notifier.py       # Sends notifications (terminal-notifier + osascript)
│   ├── config.py         # Loads settings from ~/.nudge/config.toml
│   ├── daemon/
│   │   └── __init__.py   # Main loop: while True: check file, detect, notify
│   ├── cli.py            # Commands: install, start, stop, status, logs
│   └── __main__.py       # Entry point
├── requirements.txt      # Dependencies (toml, tomli, pytest, black, flake8)
└── config/
    └── nudge.plist       # LaunchAgent config (runs daemon at startup)
```

### The Main Loop (Pseudo-code)

```python
while True:
    # 1. Check if log file has new content
    new_lines = read_new_lines_from_file()

    # 2. Check each line for questions
    for line in new_lines:
        if detector.is_question(line):
            question_found()

    # 3. If question found and cooldown expired, notify
    if enough_time_passed():
        notifier.send_notification()
        notifier.focus_ide()

    # 4. Wait 1 second before checking again
    sleep(1)
```

---

### Quiz 5: Code Structure
**Question:** Why does Nudge need a `config.py` file? What could you configure?

<details>
<summary>Click to see answer</summary>

**Answer:** Config lets users customize:
- Which log files to watch (in case Claude logs somewhere else)
- Which apps to focus (you might use iTerm instead of Ghostty)
- Notification sounds (maybe you want a different sound)
- Check interval (how often to read the file)

This makes Nudge flexible instead of hardcoded.

</details>

---

## Level 6: The Technologies (What's Under the Hood)

### Key Technologies Explained

#### **terminal-notifier**
- **What:** A macOS command-line tool
- **Does:** Creates notifications in the Mac notification center
- **Why we use it:** It's the standard way to send notifications from command line
- **Command:** `terminal-notifier -title "Nudge" -message "Question!" -actions "View"`

#### **osascript**
- **What:** A command-line tool that runs AppleScript
- **Does:** Controls Mac applications (make them focus, open files, etc.)
- **Why we use it:** Works with any Mac app without installing SDKs
- **Command:** `osascript -e 'tell application "Ghostty" to activate'`

#### **launchd**
- **What:** macOS's background task manager
- **Does:** Runs programs automatically at startup or on schedule
- **Why we use it:** So Nudge starts automatically when you log in
- **File:** `~/Library/LaunchAgents/com.nudge.daemon.plist`

#### **Python daemon**
- **What:** A Python process that runs forever
- **Does:** Loops continuously, checking for questions
- **Why we use it:** Easy to write, easy to debug, portable

---

### Quiz 6: Technologies
**Question:** Why do we use `launchd` instead of just telling users to run `nudge start` manually in their Terminal?

<details>
<summary>Click to see answer</summary>

**Answer:** Because you'd have to remember to start it every time you restart your Mac! With launchd, it starts automatically. Set it once, forget about it, and it works forever.

</details>

---

## Level 7: The Current Challenge - Multi-Terminal Support

### The Problem

Right now, Nudge works great with 1 terminal. But with 10 terminals:

```
Terminal 1: claude task1
Terminal 2: claude task2
Terminal 3: claude task3  ← ASKS A QUESTION!
...
Terminal 10: claude task10

When notification appears, Nudge focuses "Ghostty"
but it might bring Terminal 7 to focus instead of Terminal 3!
```

**Why?** Because Nudge just knows "Ghostty asked a question" but not "which Ghostty window?"

### The Solution We Need

We need to:
1. **Tag** each log entry with which terminal it came from
2. **Store** that tag in the notification
3. **Switch** to the correct terminal when clicked

---

### Quiz 7: The Problem
**Question:** If Claude asks a question in Terminal 3, but you click the notification and Terminal 7 comes to focus, what information did we lose?

<details>
<summary>Click to see answer</summary>

**Answer:** We lost the **identity of which terminal window** asked the question. The notification just said "Ghostty" but didn't say "which Ghostty window?"

</details>

---

## Level 8: Implementation Strategy (How We'll Solve It)

### Three-Part Solution

#### **Part 1: Capture Terminal Identity**
In your shell function, capture something unique about each terminal:
```bash
claude() {
  TERMINAL_ID=$(generate_unique_id)  # Could be: timestamp, random UUID, tab name
  /usr/local/bin/claude "$@" | sed "s/^/[TERMINAL:$TERMINAL_ID] /" | tee ~/.nudge/claude.log
}
```

This adds `[TERMINAL:xyz123]` to the beginning of each line.

#### **Part 2: Detector Extracts Terminal ID**
The detector reads each line and extracts the terminal ID:
```python
if "[TERMINAL:" in line:
    terminal_id = extract_terminal_id(line)
    store_with_metadata(question, terminal_id)
```

#### **Part 3: Notifier Uses Terminal ID**
When sending notification, include the terminal ID so the app knows where to switch.

---

### Quiz 8: Solution Design
**Question:** Why put the terminal ID at the **beginning** of each line instead of the end?

<details>
<summary>Click to see answer</summary>

**Answer:** Because we want to find and extract it quickly! If it's at the beginning, we can use simple fast parsing. If it's at the end, we'd have to read the whole line first. It's a performance choice.

</details>

---

## Level 9: Deep Technical Details (The Code Level)

### Regex Pattern Matching

The detective uses regex to find terminal IDs:

```python
import re

# Pattern: [TERMINAL:anything]
pattern = r'\[TERMINAL:([^\]]+)\]'

line = "[TERMINAL:term-123abc] Claude has a question?"
match = re.search(pattern, line)

if match:
    terminal_id = match.group(1)  # "term-123abc"
    print(f"Found terminal: {terminal_id}")
```

**How regex works:**
- `\[` = literal "[" character
- `TERMINAL:` = literal text
- `([^\]]+)` = capture anything that's not "]"
- `\]` = literal "]" character

---

### Quiz 9: Regex
**Question:** If a line is `[TERMINAL:ghostty-window-42] Claude: Should I use React?`, what would `match.group(1)` return?

<details>
<summary>Click to see answer</summary>

**Answer:** `ghostty-window-42`

The parentheses `()` in regex capture what's inside, so `group(1)` is the first captured group.

</details>

---

## Level 10: Integration Points (How Everything Connects)

### The Full Updated Flow

```
1. Shell function adds [TERMINAL:ID] prefix
2. Output: "[TERMINAL:abc123] Claude: Use React or Vue?"
3. Daemon reads file
4. Detector finds question AND extracts terminal ID
5. Metadata stored: {question, terminal_id: "abc123"}
6. Notifier creates notification with terminal ID
7. When user clicks, osascript targets THAT specific terminal
8. Correct window comes to focus!
```

### Changed Files

| File | Change | Why |
|------|--------|-----|
| `~/.bashrc` | Add TERMINAL_ID to output | So we know which terminal |
| `src/detector.py` | Extract terminal ID from line | So we can find and store it |
| `src/daemon/__init__.py` | Pass terminal_id to notifier | So notifier knows where to go |
| `src/notifier.py` | Use terminal_id in activation | So it focuses the right window |

---

### Quiz 10: Integration
**Question:** Which file needs to change FIRST - the shell function or the detector? Why?

<details>
<summary>Click to see answer</summary>

**Answer:** The **shell function FIRST**.

Why? Because the detector reads from the log file, which gets written by the shell function. If the shell function doesn't write the terminal ID, the detector has nothing to read! Flow matters: upstream changes before downstream changes.

</details>

---

## Next Steps

You now understand:
✅ What Nudge does (notify about Claude questions)
✅ How it works (monitor file → detect → notify)
✅ What parts exist (detector, notifier, daemon, cli)
✅ What technologies it uses (terminal-notifier, osascript, launchd)
✅ What the challenge is (multiple terminals)
✅ How we'll solve it (terminal ID tagging)
✅ Deep technical details (regex, file monitoring, osascript)

**Ready to implement?** We'll tackle it in stages, and after each stage, we'll update PROGRESS.md and this learning guide with what we accomplished!

---

## Glossary

| Term | Meaning |
|------|---------|
| **Daemon** | A background process that runs forever |
| **Notify** | Send a notification to the user |
| **Focus/Activate** | Bring a window to the front |
| **Metadata** | Extra information about data (like which terminal) |
| **Regex** | Pattern matching language for text |
| **AppleScript** | Language for controlling Mac apps |
| **osascript** | Command-line tool to run AppleScript |
| **terminal-notifier** | Command-line tool to send Mac notifications |
| **launchd** | macOS background task manager |
| **tee** | Command that both displays output AND saves to file |

---

**Remember:** Learning code is like learning a language. Start with big ideas, then zoom in on details. Ask questions (literally - ask me anything!), and don't hesitate to re-read sections. You've got this! 🚀
