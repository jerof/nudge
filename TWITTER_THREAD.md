# Building in Public: Nudge - A Simple Tool I Built

## Twitter Thread (Simple Problem → Simple Solution)

**Thread Start:**

🧵 I was losing productivity because Claude asks questions and I don't see them.

So I built a simple tool to fix it. It's called Nudge.

Here's what I learned building something small and useful.

---

**The Problem (Mine, Probably Yours Too):**

I use Claude Code in my terminal. Sometimes I tab away while Claude is thinking.

Claude finishes thinking. Claude asks me a question.

I don't notice.

Claude waits.

I eventually come back. "Oh, there's a question. Whoops."

This happens multiple times per day. I waste time hunting for which window is asking.

---

**The Simple Solution:**

Nudge sends me a notification when Claude asks a question.

Click the notification. My terminal comes to focus.

I see the question. I answer it. I move on.

That's it.

---

**How I Use It:**

```bash
# 1. Install (one time)
git clone https://github.com/jerof/nudge
cd nudge
pip install -r requirements.txt
python -m src.cli install

# 2. Update my shell (~/.bashrc)
claude() {
  /path/to/claude "$@" | tee ~/.nudge/claude.log
}

# 3. Use Claude normally
claude "write me a function"

# When Claude asks a question, I get a notification
```

Now it just works. Runs in the background. I don't think about it.

---

**What Changed:**

Before Nudge:
- Claude: "Pick option A or B"
- Me: *staring at email*
- Result: Miss question. Wasted time.

After Nudge:
- Claude: "Pick option A or B"
- *notification appears*
- Me: Click notification. Terminal appears. Answer question.
- Result: Flow state preserved. Question answered immediately.

---

**It's Surprisingly Effective:**

I've been using it daily for a week. Every single time Claude asks a question, I know immediately.

No more missed questions. No more hunting for windows.

The time I save is real. Maybe 30 minutes per day. That adds up.

---

**How It Works (Simple Version):**

1. I pipe Claude output to a log file
2. A background daemon watches that log file
3. When it sees a question, it sends a notification
4. I click the notification
5. Terminal comes to focus

200 lines of Python. No external services. No cloud. Runs on my machine.

---

**The Fun Part (Multi-Terminal):**

I have multiple terminals running Claude in parallel.

Old problem: Click notification, wrong terminal comes to focus.

How I fixed it: Each terminal gets tagged with a unique ID. When I click notification, it focuses the EXACT terminal that asked.

Tested it. Works perfectly. Boring problem. Boring solution. But it works.

---

**Why I'm Sharing This:**

This isn't a groundbreaking product. It's a tool I built for myself.

But it's useful. It's simple. It's free. It solves a real problem.

If you use Claude Code and miss questions, it will probably help you too.

---

**Try It:**

```bash
git clone https://github.com/jerof/nudge
cd nudge
pip install -r requirements.txt
python -m src.cli install
```

Or check the docs:
https://github.com/jerof/nudge

---

**What I Learned Building Something Simple:**

1. The best features solve problems you actually have
   (Not problems you imagine other people might have)

2. Simple tools get used. Complex tools collect dust.
   (Nudge is 300 lines. That's it.)

3. Shipping early matters more than shipping perfect
   (I could optimize forever. Instead I released when it worked.)

4. Honest limitations beat polished promises
   (I tell people what Nudge doesn't do. That builds trust.)

5. Building in public > building in silence
   (Sharing the journey helps others build too)

---

**One Week In:**

Nudge has saved me probably 2+ hours of wasted time.

That's real value from a tool I built in an afternoon.

If you're running Claude Code regularly, try it. See if it helps.

If it does, tell me. If it breaks, tell me that too.

Let's build together.

---

GitHub: https://github.com/jerof/nudge
README: Full docs on how to use

Simple tool. Real problem. Real solution. 🚀

#BuildingInPublic #SmallTools #Claude #Productivity #MacOS
