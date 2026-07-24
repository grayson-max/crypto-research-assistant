# Setting This Up (and Taking It Off Your Computer)

You don't need to know anything about coding or AI to follow this. Just
do each step in order, in the order it's written. It should take about
10 minutes.

This only works on a **Mac**.

**Contents**
1. Setting it up
2. Changing settings later — schedule time, delivery folder
3. Changing what's in the brief — new data, charts, wording
4. Taking it off your computer
5. Common problems and how to fix them

---

# 1. Setting It Up

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

   **Don't put it inside Desktop, Documents, or Downloads.** macOS
   blocks background scheduling from touching files in those three
   folders unless you separately grant access in System Settings, so
   the daily automatic brief would silently stop working with no error
   message telling you why. Your Home folder itself, or any other
   regular folder, is fine.
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

---

# 2. Changing Settings Later

If you ever want to change what time the brief runs, or the iCloud
Drive folder it's delivered to, you don't need to reinstall anything.

## Step 1: Open Terminal and go to the project folder

1. Open Terminal the same way as in 1, Step 1.
2. Type this and press Enter:
   ```
   cd crypto_research_assistant
   ```

## Step 2: Run the settings tool

1. Type this and press Enter:
   ```
   ./configure.sh
   ```
2. It first shows you what's currently set, for example:
   ```
   Current settings:
     Coins tracked: BTC, ETH, SOL
     Schedule time: 08:00
     Delivery folder (iCloud Drive): CryptoBriefs
   ```
3. It then asks for a new schedule time, showing the current one in
   brackets:
   ```
   New schedule time [08:00]:
   ```
   - To **change it**: type the new time in 24-hour format (e.g. `17:30`
     for 5:30 PM) and press Enter.
   - To **keep it the same**: just press Enter without typing anything.
4. It asks the same way for a new delivery folder name — type a new
   name, or press Enter to keep the current one.
5. It saves your answers and reschedules the daily run automatically.
   You'll see a confirmation like:
   ```
   Done. Briefs will now be delivered to iCloud Drive > CryptoBriefs at 17:30 daily.
   ```

That's it — nothing else needs restarting, and your saved keys and past
briefs are untouched.

**Example:** to move the daily brief from 8:00 AM to 5:30 PM, run
`./configure.sh`, type `17:30` when asked for the new schedule time,
then press Enter at the folder prompt to leave it as-is.

(Changing which coins are tracked isn't a guided prompt yet — that
means editing a settings file directly, which is more technical. Ask
whoever set this up for you if you need that changed.)

---

# 3. Changing What's in the Brief

Everything above covers running the brief as it already is. If you want
it to actually say or show something different — track one more data
point, add a small chart, shorten a section — that's not a settings
toggle like 2. It's a small code change, and the easiest way to
make one without learning to code yourself is to ask an AI assistant
called **Claude Code** to make it for you, in plain English.

## Step 1: What Claude Code actually is

Think of it like texting a request to someone who can read and edit
this project's code — except instead of a person, it's Claude (the same
AI that writes the brief itself), and instead of texting, you type in
Terminal. You describe what you want changed in plain English; it makes
the change and tells you what it did.

## Step 2: Install it (one time)

1. Go to **claude.com/claude-code** in your browser and follow the
   install instructions there for your Mac.
2. You'll need your own Claude account to use it — this is separate
   from the Anthropic key you set up in 1, Step 2. That key only
   lets the pipeline *silently* call Claude in the background; using
   Claude Code is *you* directly chatting with it, which is a different
   kind of access.

## Step 3: Open it inside this project

1. Open Terminal and go to the project folder, same as always:
   ```
   cd crypto_research_assistant
   ```
2. Type:
   ```
   claude
   ```
3. Wait for it to start up — you'll see a prompt where you can type a
   message.

## Step 4: Ask for the change, in plain English

Just describe what you want. Some examples:
- *"Add a data point showing each coin's 7-day trading volume trend."*
- *"Add a small chart showing Bitcoin's price over the last 7 days."*
- *"Make the headlines section shorter — 2 items per coin instead of 4."*

It may ask a clarifying question or show you what it's about to change
before doing it — that's normal, just answer or confirm.

## Step 5: See the result

Ask it directly: *"Regenerate today's brief so I can see the change."*
It'll run the pipeline and you can check the result the same way as
always — in `reports/` or the delivered copy in iCloud Drive.

## If you don't like the result

Just say so — *"undo that last change"* works, because this project
folder is tracked with a tool called **git** that remembers every past
version, like a safety net. Nothing you ask for here is permanent or
risky to try.

---

# 4. Taking It Off Your Computer

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

# 5. Common Problems and How to Fix Them

Nothing here can damage your computer — worst case, a brief doesn't get
generated one day. Here are the issues most likely to come up, and
exactly what to do about each one.

### "Permission denied" when running `./install.sh` (or any `./` command)

This means the file isn't marked as "runnable" yet. Fix it once with:
```
chmod +x install.sh configure.sh uninstall.sh
```
Then try the original command again.

### macOS pops up asking for permission to access files/folders

The first time these scripts touch iCloud Drive or your saved settings,
macOS may ask something like *"Terminal" wants access to files in your
Documents folder*. Click **OK** or **Allow** — this is expected and
required for briefs to be delivered.

If you accidentally clicked **Don't Allow** and things stopped working:
go to  **System Settings → Privacy & Security → Files and Folders**
(on some macOS versions: **Full Disk Access**), find **Terminal** in
the list, and turn it on.

### During install, it says a key "failed to validate"

- **Anthropic key failed**: usually means either the key was copied
  wrong (go back to console.anthropic.com and copy it again, carefully
  — no extra spaces), or a payment method hasn't been added yet on that
  site (Anthropic's key won't work until billing is set up, even though
  the cost itself is small).
- **NewsAPI key failed**: almost always a copy/paste typo — go back to
  your NewsAPI account page and copy it again.

After fixing it, just run `./install.sh` again — it's safe to re-run
and won't duplicate anything already set up.

### No brief showed up today

Check these in order:

1. **Was your Mac asleep or off around the scheduled time (and for the
   30 minutes after)?** If so, it'll catch up automatically the next
   time your Mac is awake — no action needed.
2. **Look at the log file for an error message.** In Finder, open the
   `crypto_research_assistant` folder, find the file named `cron.log`,
   and double-click it to open it in TextEdit. Scroll to the very
   bottom (the most recent entry) and look for:
   - **Anything mentioning "timeout" or "connection"** → the internet
     was briefly down when it tried to run. Safe to ignore — it'll
     succeed the next scheduled run, or you can generate one manually
     (see "Want a brief right now instead of waiting?" in 1).
   - **Anything mentioning "401" or "authentication" near "anthropic"**
     → your Anthropic key has expired or its billing lapsed. Check
     console.anthropic.com, fix it there, then generate a brief
     manually to confirm it's working again.
   - **"Missing required API key(s)"** → your `.env` file is missing or
     got moved/deleted. Run `./install.sh` again to re-enter your keys.
3. **Check iCloud Drive is turned on.** Go to **System Settings → your
   name at the top → iCloud → iCloud Drive** and make sure it's
   switched on. Without it, briefs still generate and save on this
   Mac, but won't sync to your phone or other devices.

### It's generating briefs, but they're not showing up on my phone/other devices

That's almost always the iCloud Drive check above (#3) — the brief is
being created fine, it just isn't syncing anywhere else yet.

### None of the above matches what you're seeing

Copy the exact text Terminal (or `cron.log`) showed you and send it to
whoever gave you this project.
