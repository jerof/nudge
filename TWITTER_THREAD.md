# Building in Public: How I Built Nudge (Multi-Terminal Claude Notifications)

## Twitter Thread

**Thread Start:**

🧵 I'm building in public. Here's how I went from "Claude asks questions and I miss them" to a fully-working multi-terminal notification daemon in macOS.

The problem: You're using Claude Code in your terminal but don't notice when it asks a question. You're looking at a different window. You miss the question entirely.

The solution: Nudge. A lightweight daemon that:
✅ Detects when Claude asks a question
✅ Sends you a macOS notification (top-right corner)
✅ Click it → your terminal comes to focus
✅ Runs invisibly in the background

---

**Implementation:**

Built the MVP in one session:
- Python daemon that monitors log files
- Pattern matching to detect "AskUserQuestion" tool calls
- terminal-notifier for macOS notifications
- osascript/AppleScript to bring terminals to focus
- launchd integration for auto-start on login

Result: It works! But there's a problem...

---

**The Real Problem (Multi-Terminal):**

If you have 10 Ghostty terminals running Claude in parallel, and one asks a question, clicking the notification might activate TERMINAL 7 instead of TERMINAL 3.

Why? The daemon knew "Ghostty asked a question" but not "WHICH Ghostty window?"

This is where it got interesting. I didn't just fix it—I documented the entire learning journey.

---

**The Learning Approach:**

Instead of shipping silently, I created LEARNING.md using a Socratic method:
- Level 1-2: Big picture concepts
- Level 3-4: How components connect
- Level 5-6: Code structure and technologies
- Level 7-10: The multi-terminal challenge
- Level 11: Full implementation walkthrough

Each level includes quiz questions. You learn by building understanding, not memorizing.

Inspired by how I learn best: upload source material + ask for progressive explanations from high-level to incredibly low-level detail.

---

**The Roadmap:**

Created ROADMAP.md with 5 implementation steps:

STEP 1: Add unique terminal ID to shell wrapper
- Each Claude output gets tagged: `[TERM:term-1762552270-33202-29167]`
- Simple but effective

STEP 2: Detector extracts terminal ID
- Uses regex: `r'\[TERM:([^\]]+)\]'`
- Returns the ID for tracking

STEP 3: Daemon passes terminal ID through flow
- Changed return type from `bool` to `Optional[str]`
- Terminal ID flows from detection to notification

STEP 4: Notifier groups notifications
- Uses terminal-notifier's `-group` flag
- All notifications from same terminal grouped together

STEP 5: Test with multiple terminals
- Added 3 simultaneous questions from different terminals
- All detected correctly ✅

---

**The Result:**

Phase 2 implementation complete. Now when:
- Terminal 1, 2, 3 ask questions simultaneously
- Each notification is grouped by terminal ID
- Clicking notification → focuses the CORRECT terminal

Tested with real scenarios. Works.

---

**What I Learned About Building in Public:**

1. **Documentation is a feature**
   - LEARNING.md forced me to explain my thinking
   - Made the code better (had to understand it deeply)
   - Others can now learn from it

2. **Roadmaps enable handoff**
   - Created ROADMAP.md so any Claude instance could pick up work
   - Or any human developer could continue
   - The "what to do next" is crystal clear

3. **Progress tracking matters**
   - Updated PROGRESS.md after every step
   - Shows status, test results, limitations
   - Accountability (to myself, to anyone watching)

4. **Learning frameworks are powerful**
   - Socratic method > just code comments
   - Progressive complexity helps understanding
   - Quiz questions confirm comprehension

---

**Open Questions (Future):**

Phase 3 ideas (not built yet):
- Question preview text in notifications
- Response buttons (Yes/No/Other)
- Dashboard UI for pending questions
- Non-Ghostty terminal support

Should I build these? Depends on whether multi-terminal support solves the original problem.

---

**The Stack:**

- Python 3.8+
- terminal-notifier (macOS native)
- osascript/AppleScript (window management)
- launchd (background service)
- TOML configuration
- Git (with clean commit history)

All documented in CODE.md with architecture decisions.

---

**Why This Matters:**

The building in public movement is about:
✅ Showing your work (not just finished products)
✅ Documenting decisions (not just code)
✅ Teaching while building (not after)
✅ Creating artifacts others can learn from

Nudge isn't a billion-dollar idea. But it's real, it solves a real problem, and it shows thinking clearly.

---

**Want to learn how this works?**

Start with LEARNING.md: https://github.com/yourname/nudge/blob/main/LEARNING.md

Then read ROADMAP.md to see how multi-terminal support was designed and implemented.

The code is on GitHub. The thinking is documented. The process is transparent.

That's building in public.

---

**Final thought:**

"Simple scales, fancy fails."

Nudge is simple:
- Watch a log file
- Detect questions
- Send notifications
- Focus window

But the documentation, learning journey, and design thinking behind it? That's where the real work is.

If you're building something, document your thinking. Your future self (or someone else) will thank you.

---

Links:
- GitHub: https://github.com/jerof/nudge
- Portfolio: https://nikhilsamuel.me/side-gigs.html

Built by @nikhilsamuel
Learn from @ClaudeAI
Share your work 🚀

#BuildingInPublic #OpenSource #MacOS #DevTools #Claude #Learning
