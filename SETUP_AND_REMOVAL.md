# Setting This Up (and Taking It Off Your Computer)

You don't need to know anything about coding or AI to follow this. Just
do each step in order, in the order it's written. It should take about
10 minutes.

This only works on a **Mac**.

---

# Part 1: Setting It Up

## Step 1: Open Terminal

Terminal is an app already on your Mac — it lets you type commands
instead of clicking things.

1. Press `Command (⌘)` + `Space bar` at the same time. A search box pops up.
2. Type: `Terminal`
3. Press `Enter`.

A plain window with white or black background will open, showing some
text ending in a `$`. That's where you'll type everything below.

## Step 2: Get two free/cheap accounts set up

Before installing anything, you need two "keys" — think of a key as a
password that lets this tool fetch data on your behalf. You'll get
these from two websites.

**Key 1 — Anthropic (this is what writes the brief itself)**

1. Go to **console.anthropic.com** in your browser and sign up.
2. You'll need to add a card — this one is pay-as-you-go, but for one
   short brief a day it typically costs just a few cents a month.
3. Once signed in, find **"API Keys"** in the left-hand menu, click
   **"Create Key"**, and copy the long string of letters/numbers it
   gives you. Paste it somewhere temporarily (like a Notes app) — you'll
   need to paste it into Terminal in Step 4.

**Key 2 — NewsAPI (this is what finds headlines — it's free)**

1. Go to **newsapi.org/register** in your browser and sign up.
2. Once signed in, copy your API key from your account page and save it
   next to the first key.

## Step 3: Get the project onto your computer

You should have received a file called **`crypto_research_assistant.zip`**
(by AirDrop, email, or a file-sharing link).

1. Find it in your **Downloads** folder (or wherever it landed) and
   double-click it. It'll unzip into a regular folder named
   `crypto_research_assistant`.
2. Move that folder somewhere you'll remember — your **Home** folder
   (the one with the little house icon in Finder) is a good default.
3. Back in Terminal, type this and press Enter, to move into that folder:
   ```
   cd crypto_research_assistant
   ```
   If Terminal says "No such file or directory," you likely moved the
   folder somewhere else — type `cd ` (with a trailing space, no Enter
   yet), then drag the folder from Finder into the Terminal window,
   which fills in the correct path for you, then press Enter.

If Terminal shows an error about "git" not being found, a small popup
will offer to install it for you — click **Install**, wait for it to
finish, then repeat Step 3.

## Step 4: Run the installer

1. In Terminal, type exactly this and press Enter:
   ```
   ./install.sh
   ```
2. It will ask you a series of questions, one at a time. For each one,
   just type your answer and press Enter — or if you see something in
   `[brackets]`, pressing Enter by itself uses that as the default.
3. When it asks for your Anthropic key or NewsAPI key, paste the one
   you saved in Step 2 and press Enter. (Right-click → Paste, or
   `Command (⌘) + V`.)
4. It will check that both keys actually work. If one fails, it'll tell
   you clearly which one and why — usually a typo. Just run
   `./install.sh` again to retry.
5. When you see `=== Setup complete ===`, you're done.

## What happens now

Every day at the time you chose (8:00 AM by default), this will
automatically:
- Check today's crypto prices and news
- Have Claude write a short brief about it
- Save a nicely formatted copy into your **iCloud Drive**, in a folder
  called **CryptoBriefs** (or whatever name you chose)

You don't need to keep Terminal open, and you don't need to do anything
else — it runs on its own, even if you're not using your computer at the
time, as long as your Mac isn't asleep or turned off.

To see a brief right away instead of waiting, type this in Terminal
from inside the project folder:
```
.venv/bin/python3 main.py
```

## Changing your settings later

If you want to change what time it runs, or the delivery folder name,
type:
```
./configure.sh
```
and answer the same style of questions again.

---

# Part 2: Taking It Off Your Computer

If you ever want to stop this — for any reason, no explanation needed —
here's how, and it's built to be careful about not deleting things you
might want to keep.

## Step 1: Open Terminal and go to the project folder

1. Open Terminal the same way as Step 1 above.
2. Type this and press Enter:
   ```
   cd crypto_research_assistant
   ```
   (If you get an error saying that folder doesn't exist, it may be
   somewhere else — ask whoever set this up for you where it's located.)

## Step 2: Run the uninstaller

1. Type this and press Enter:
   ```
   ./uninstall.sh
   ```
2. It will immediately turn off the daily automatic brief — this part
   happens without asking, since it's completely safe to undo (you'd
   just run `./install.sh` again).
3. Then it will ask you three separate yes/no questions, one at a time,
   about whether to also delete:
   - Some technical setup files (fine to delete — `y`)
   - Your saved keys/settings (say `n` if you might reinstall later and
     don't want to look up your keys again)
   - Your saved past briefs (say `n` if you want to keep reading them)

   For each question, type `y` and press Enter to say yes, or `n` and
   press Enter to say no — or just press Enter by itself for "no," which
   is the safe default.

## What's left afterward

The project folder itself stays on your computer either way — nothing
about the uninstaller deletes it automatically. If you want it gone
completely, you can drag the `crypto_research_assistant` folder to the
Trash yourself once you're done, the same way you'd delete any other
folder.

---

## If something goes wrong

Nothing here can damage your computer — worst case, a brief doesn't get
generated one day. If a step doesn't work the way this describes, copy
the exact text Terminal showed you and send it to whoever gave you this
project.
