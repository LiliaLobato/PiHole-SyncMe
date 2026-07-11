# nightBlock — Pi-hole nightly curfew

Blocks a **separate, editable** list of domains overnight (default 10pm→7am, editable per day) and lifts it in the morning, without touching the always-on Pi-hole lists. The Pi pulls this repo on a cron and applies it.

## Edit these two files (from your laptop, then `git push`)
- **`nightBlockList.txt`** — the domains to curfew. One per line; `#` = comment.
  - exact FQDN → exact deny (`www.instagram.com`)
  - contains regex chars `^ $ | ? * + ( ) [ ] { } \` → regex deny
  - force regex with `re:<pattern>`; bare `.`/`-` are *not* regex
- **`schedule.json`** — per-day `block`/`unblock` times (24h), `timezone` (IANA), and `enabled`.
  - overnight window; assumes `unblock < block`
  - skip a night: set that day's times to `null`
  - kill switch: top-level `"enabled": false`

Changes take effect on the Pi within one cron tick (10 min).

## How it works
`apply.py` (run by cron on the Pi) each tick:
1. `git pull` (offline-safe — falls back to last pulled copy)
2. reconcile `nightBlockList.txt` into Pi-hole `domainlist` deny rows tagged `[NightCurfew]`, linked to the **Default group (0)** = all devices
3. compute ON/OFF for *now* from `schedule.json`
4. toggle the tagged rows' `enabled`
5. **only if something changed**, run `pihole reloadlists`

Idempotent & self-healing (survives reboots; re-asserts correct state every tick). "When" (the toggle) is decoupled from "who" (group), so scoping to specific devices later needs no code change — just move the rows to a custom group + assign clients.

## Snooze (need the blocked sites tonight)
```bash
sudo python3 apply.py --snooze    # curfew OFF until it would next lift; auto-resumes tomorrow night
sudo python3 apply.py --resume    # cancel the snooze right now
```
`--snooze` writes `/opt/pihole-nightcurfew/snooze_until` (a timestamp = the next morning the curfew would lift). Every cron tick honors it — so the curfew stays **off for the rest of tonight** and comes back **on its normal schedule tomorrow**, no manual step needed. `--resume` deletes the marker. `--force-on`/`--force-off` ignore snooze (manual test overrides). From the laptop, `GeneralScripts/PiHoleCurfew.ps1` runs these over SSH.

## Testing (no live Pi needed for logic)
```bash
# 1) pure logic (schedule math + parsing) — laptop
python test_schedule.py

# 2) offline dry-run against a COPY of gravity.db — laptop, writes nothing
#    get a consistent copy:  pihole-FTL sqlite3 /etc/pihole/gravity.db ".backup /tmp/g.db"  (then scp it)
python apply.py --engine python --db g.db --dry-run --force-on
python apply.py --engine python --db g.db --dry-run --now "2026-07-10 23:30"

# 3) real block/unblock — ON THE PI, then ping from the laptop
sudo python3 apply.py --force-on    # laptop: nslookup www.instagram.com 10.0.0.174 -> 0.0.0.0
sudo python3 apply.py --force-off   # laptop: nslookup www.instagram.com 10.0.0.174 -> real IP
```

## Flags
`--engine ftl|python` (default `ftl` = Pi-hole's `pihole-FTL sqlite3`; `python` = stdlib sqlite3, **test only**) ·
`--db PATH` · `--dry-run` · `--force-on` · `--force-off` · `--snooze` · `--resume` · `--now "YYYY-MM-DD HH:MM"` · `--no-pull`

## Install on the Pi
`bash install.sh` — clones to `/opt/pihole-nightcurfew`, backs up `gravity.db`, and prints the test + cron-enable commands. It does **not** schedule anything until you enable cron yourself.
