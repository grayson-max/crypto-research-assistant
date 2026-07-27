# The Installer, Explained in Plain Language

This file explains what `bootstrap.sh`, `install.sh`, `configure.sh`,
and `uninstall.sh` actually do, step by step, and defines every
technical term along the way. It's written for someone setting this
project up for the first time who isn't necessarily a programmer.

## The big picture

This project checks crypto prices and news once a day, has Claude write
a short research brief about it, and saves that brief somewhere you can
read it. To do that *automatically, every day, without you running a
command yourself*, a few things need to be set up on your computer once.

For a first-time install, all you actually run is one line in Terminal:

```
curl -fsSL https://raw.githubusercontent.com/grayson-max/crypto-research-assistant/main/bootstrap.sh | bash
```

That downloads and runs `bootstrap.sh`, which asks for your two API keys
up front (checking each one works before anything else happens), then
downloads the project and hands off to `install.sh` to finish the rest.
You never need to manually download a zip file or `cd` into a folder
first — see `READ_ME_instructions.html` for the full walkthrough.

Four scripts, four jobs:

| Script | When you run it | What it does |
|---|---|---|
| `bootstrap.sh` | Once, via the one-line command above | Collects & validates API keys, downloads the project, then runs `install.sh` |
| `install.sh` | Automatically, at the end of `bootstrap.sh` (or on its own, if re-running later) | Sets up the Python environment, dependencies, and daily schedule |
| `configure.sh` | Any time later | Changes your schedule or where briefs get delivered |
| `uninstall.sh` | If you ever want to stop | Removes the automatic daily run, asks before deleting anything else |

## What is a "script"?

A script is just a text file full of commands, meant to be run all at
once instead of typed one at a time. `install.sh` is a **shell
script** — a script written in the language your Mac's Terminal
understands directly. You run it by typing `./install.sh` in Terminal,
from inside the project folder.

## Running `install.sh` — step by step

### Step 1-2: Python and the "virtual environment"

The project is written in Python, a programming language. Step 1 checks
Python is installed. Step 2 creates a **virtual environment** (the
folder `.venv`) — think of it as a private, sealed toolbox just for this
project. It holds exactly the tool versions this project needs, so they
can't clash with anything else Python-related on your computer, and so
uninstalling later is as simple as deleting one folder.

### Step 3: Installing dependencies

**Dependencies** are other people's code that this project relies on
instead of reinventing (for example, code that knows how to talk to a
website's API). `requirements.txt` lists them; this step downloads and
installs them into the `.venv` toolbox from step 2.

### Step 4: Your preferences (`config.json`)

When installed via the one-line `bootstrap.sh` command, this step is
silent: it copies `config.example.json` straight to `config.json`,
which tracks Bitcoin, Ethereum, and Solana, generates at 8:00 AM, and
delivers to an iCloud Drive folder named `CryptoBriefs`. Nothing is
asked here — that's what keeps the install down to one command. Change
any of it afterward by running `./configure.sh` (see below).

Your `config.json` is **not** shared if you ever share this project's
code with someone else (e.g. by putting it on GitHub) — each person who
installs their own copy gets their own `config.json` with their own
choices. (The technical term for "don't share this file" is that it's
**git-ignored** — see `.gitignore`.)

### Step 5: API keys (`.env`)

This step is handled by `bootstrap.sh`, before `install.sh` even runs
— it's the very first thing that happens, so a bad key is caught before
anything else is downloaded or installed. `install.sh` sees the `.env`
file `bootstrap.sh` already created and skips this step entirely; it
only prompts for keys itself if you ever run `install.sh` directly in a
folder that has no `.env` yet.

An **API** (Application Programming Interface) is how one program asks
another program for data over the internet — in this case, asking
CoinGecko for prices, NewsAPI for headlines, and Anthropic (the company
that makes Claude) to write the brief text. An **API key** is like a
password that proves the request is coming from you, so the company
providing the API can track usage and (for paid ones) bill you correctly.

**You will be asked for two keys:**

1. **Anthropic API key** (`console.anthropic.com`) — **paid, billed per
   use.** This is what lets the code call Claude programmatically to
   write each day's brief. For one short brief a day, the cost is a few
   cents at most, but it does require adding a payment method on that
   site.

   **Important distinction, because this trips people up:** this key is
   *not* the same thing as a Claude.ai login, and it's *not* the same as
   having Claude Code installed. Those let *you, a person,* type
   messages to Claude in a chat window or terminal. This key lets *this
   code* silently call Claude in the background, with no chat window
   involved, and is billed completely separately. Having one does not
   give you the other.

2. **NewsAPI key** (`newsapi.org`) — **free**, up to 100 requests per
   day, way more than this project needs.

Two free data sources need no key at all: CoinGecko (prices) and
alternative.me (the Fear & Greed sentiment index).

The installer doesn't just save these keys — it makes one small test
request with each one, right then, to confirm they actually work. If a
key is wrong, you'll find out immediately with a clear message, instead
of finding out three days later when you notice no brief showed up.

Both keys get saved into a file called `.env` (short for
"environment" — a standard name for "secrets live here"). Like
`config.json`, `.env` is git-ignored — it never gets shared if you share
the project's code.

### Step 6: Scheduling with "cron"

**cron** is a feature built into every Mac (and Linux computer) that
works like a recurring alarm clock for commands — "run this exact
command at this exact time, every day, forever, with nobody watching."
This step tells cron to run the brief-generating code at whatever time
you chose in Step 4.

cron's one limitation: if your Mac is asleep at the scheduled time, that
day's alarm is simply skipped — cron doesn't run *late*, it just doesn't
run.

### Step 7: The catch-up check with "launchd"

**launchd** is Apple's more flexible built-in scheduler — more capable
than cron, but more fiddly to configure directly. Here, it's used for
one specific job: every 30 minutes, quietly check "does today's brief
exist yet?", and if not, generate it. This is what catches the case from
Step 6 — if your Mac was asleep at 8:00 AM, you'll still get today's
brief within about 30 minutes of waking it up, instead of not at all.

launchd needs a small configuration file to know what to run and how
often — that's the `.plist` file this step creates in
`~/Library/LaunchAgents/`, a standard system folder for these
configurations.

## `configure.sh` — changing your mind later

Run `./configure.sh` any time. It shows your current settings, asks for
new values (just press Enter to keep anything the same), saves the
updated `config.json`, and re-does *only* the cron scheduling step
(Step 6 above) — it doesn't touch your `.venv`, your API keys, or your
saved briefs. Changing which coins are tracked isn't a guided prompt yet
— edit the `"coins"` section of `config.json` directly (see
`config.example.json` for the exact shape each entry needs), then run
`configure.sh` so the schedule stays in sync.

## `uninstall.sh` — turning it off

Run `./uninstall.sh` any time you want to stop.

**It always does two things first, no questions asked**, because these
are 100% safe to reverse (you'd just run `install.sh` again):
1. Removes the cron alarm from Step 6
2. Removes the launchd catch-up check from Step 7

After that, daily automatic generation is fully stopped.

**Then it asks you, one at a time, before touching anything else** —
because these hold things you might want to keep:
- Delete the `.venv` toolbox? (safe to say yes — easily rebuilt by
  running `install.sh` again)
- Delete your API keys and preferences (`.env`, `config.json`)? (say no
  if you might reinstall later and don't want to re-enter your keys)
- Delete your saved briefs (`reports/`)? (say no if you want to keep the
  history)

It never deletes the project folder itself, and never has a "delete
everything, don't ask" shortcut — you're always in control of what
actually gets removed.

## Asking Claude about your past briefs

Once this is installed, you can open **Claude Code** (Anthropic's
command-line tool for using Claude) inside this project folder and just
ask it things like *"how did BTC do this week"* or *"summarize the
sentiment trend this month."*

Two files make that work well from your very first question, instead of
Claude having to explore the whole project cold every time:

- **`CLAUDE.md`** (in the project's main folder) — a plain-language
  cheat sheet that tells Claude where the daily briefs are saved
  (`reports/brief_YYYY-MM-DD.md`, one file per day) and reminds it to
  answer using the same careful, research-only language the briefs
  themselves use (no "buy," "sell," or "should," no price predictions)
  — so an answer typed in chat holds to the same standard as a written
  brief.
- **`.claude/skills/askbrief/`** — a pre-written set of instructions
  (a **skill**, in Claude Code terminology) specifically for questions
  that span *multiple* days, like "this week" or "this month" — it
  knows to check which dated files actually exist and read all of them
  before answering, rather than only looking at today's.

Reminder on the API key question from Step 5: asking Claude questions
this way uses your own Claude Code / Claude.ai access, not the
`ANTHROPIC_API_KEY` saved in `.env`. That key is only used by the
background pipeline code — it doesn't log you into anything.
