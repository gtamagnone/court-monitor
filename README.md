🎾 Court Padel Monitor

Automatic padel court availability monitor for ATC Sports, running through GitHub Actions.

The monitor periodically checks the availability of Esandi Padel, Bariloche, detects newly available courts within the configured days and time range, and sends a notification through Telegram.

No computer or personal server needs to remain powered on.

---

🚀 How It Works

                 GitHub Actions
                       │
                 Every 5 minutes
                       │
                       ▼
                ┌─────────────┐
                │   ATC API   │
                └──────┬──────┘
                       │
                Available slots
                       │
                       ▼
                Filter by day
                  + time range
                       │
                       ▼
                Compare against
                 previous state
                       │
              ┌────────┴────────┐
              │                 │
          No changes       New availability
              │                 │
              ▼                 ▼
           Finish             Telegram

The monitor does not send a notification every time it finds an available slot.

It only sends a notification when a slot that was previously unavailable becomes available.

For example:

10:00 → Wednesday 20:00 unavailable
10:05 → Wednesday 20:00 unavailable
10:10 → Wednesday 20:00 AVAILABLE
                         ↓
                    📲 Telegram
10:15 → Wednesday 20:00 available
                         ↓
                    No notification

---

📁 Project Structure

padel-monitor/
│
├── atc.py
├── monitor.py
├── notifier.py
├── config.json
├── state.json
├── requirements.txt
│
└── .github/
    └── workflows/
        └── monitor.yml

"atc.py"

Handles communication with the ATC Sports API and retrieves available slots.

It currently monitors the Esandi Padel sports club:

sportclub_id = 1684

The API provides information such as:

- Court
- Date
- Start time
- Duration
- Price

---

"monitor.py"

The main application.

It is responsible for:

1. Reading "config.json".
2. Determining which days should be checked.
3. Querying ATC.
4. Filtering slots according to the configured time range.
5. Comparing current availability against "state.json".
6. Detecting newly available slots.
7. Sending Telegram notifications.
8. Updating the stored state.

---

"notifier.py"

Contains the Telegram integration.

Telegram credentials are not stored in the source code. They are provided through environment variables:

TELEGRAM_TOKEN
TELEGRAM_CHAT_ID

---

"config.json"

Contains the monitoring configuration.

Example:

{
  "venue": "Esandi Padel",
  "sportclub_id": 1684,
  "watch": {
    "days": [
      "wednesday",
      "thursday"
    ],
    "from": "16:30",
    "to": "21:00"
  }
}

Configuration Parameters

Parameter| Description
"venue"| Name of the venue
"sportclub_id"| ATC sports club identifier
"watch.days"| Days of the week to monitor
"watch.from"| Start of the time range
"watch.to"| End of the time range

Days must be specified in English:

monday
tuesday
wednesday
thursday
friday
saturday
sunday

---

💾 "state.json"

Stores the availability state from the previous successful check.

Its purpose is to prevent duplicate notifications.

Example:

{
  "2026-08-05": [
    "Court 4|2026-08-05T20:30:00-03:00"
  ]
}

The file is persisted between GitHub Actions runs using GitHub Actions Cache.

---

📦 Dependencies

Dependencies are defined in "requirements.txt":

requests

The project does not use Selenium or Playwright.

Availability is retrieved directly from the API used by ATC Sports.

---

🤖 GitHub Actions

The monitor runs automatically using:

.github/workflows/monitor.yml

The current schedule is:

on:
  schedule:
    - cron: "*/5 * * * *"

  workflow_dispatch:

This provides:

- ⏱️ Automatic execution approximately every 5 minutes
- ▶️ Manual execution from GitHub

Manual Execution

From GitHub:

Actions
  ↓
Padel Monitor
  ↓
Run workflow

Automatic Execution

No computer needs to remain powered on.

GitHub temporarily creates a virtual machine to execute the workflow, runs the monitor, and then terminates the environment.

«GitHub Actions may introduce some delay compared to the exact "cron" schedule. A workflow scheduled every 5 minutes may therefore not start exactly at "00", "05", "10", etc.»

---

🔐 GitHub Secrets

Telegram credentials must never be included in:

- "monitor.py"
- "config.json"
- "notifier.py"
- "README.md"
- Any version-controlled file

They must be configured as Repository Secrets in GitHub:

TELEGRAM_TOKEN
TELEGRAM_CHAT_ID

Path:

Repository
  ↓
Settings
  ↓
Secrets and variables
  ↓
Actions
  ↓
New repository secret

The workflow exposes them to the application through environment variables.

---

📲 Telegram

When a new slot becomes available within the configured range, the bot sends a notification.

Example:

🎾 A SLOT JUST OPENED!

📍 Esandi Padel
📅 Wednesday 12/08
🕐 20:30
🏟️ Court 4

👉 Open ATC Sports to book it.

---

🛡️ Error Handling

The monitor is designed to avoid false notifications.

If ATC fails to respond or an error occurs during a query:

❌ ATC query failed
       ↓
Previous state is preserved
       ↓
Next execution retries

This prevents a temporary ATC error from being interpreted as if all previously available slots had disappeared.

---

🧪 Running Locally

To run the monitor manually:

pip install -r requirements.txt
python monitor.py

For Telegram notifications to work locally, define:

Linux / macOS

export TELEGRAM_TOKEN="..."
export TELEGRAM_CHAT_ID="..."

Windows PowerShell

$env:TELEGRAM_TOKEN="..."
$env:TELEGRAM_CHAT_ID="..."

Then:

python monitor.py

---

🔄 Availability Detection

The monitor distinguishes between:

Slot Already Available

Previous state: 20:30 available
Current state:  20:30 available

→ No notification

Newly Released Slot

Previous state: 20:30 unavailable
Current state:  20:30 available

→ 📲 Send notification

ATC Error

Previous state: 20:30 available
Query:          ERROR

→ Preserve previous state
→ Do not notify

---

🔮 Future Improvements

Potential future features:

- [ ] Direct link to the ATC booking page from Telegram.
- [ ] Book button directly in the Telegram notification.
- [ ] Support for multiple venues.
- [ ] Support for multiple time ranges per day.
- [ ] Telegram commands to modify monitoring settings.
- [ ] Daily availability summary.
- [ ] Statistics showing when slots are most likely to become available.
- [ ] Automatic booking, if technically feasible and permitted by ATC.

---

📜 License

Personal project for monitoring padel court availability.

ATC Sports and all other services used by this project belong to their respective owners.