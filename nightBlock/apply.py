#!/usr/bin/env python3
"""PiHole AutoBlocker - reconcile the [NightCurfew] domainlist to match
nightBlockList.txt and toggle it on/off per schedule.json.

Two DB engines:
  ftl    (default, PRODUCTION on the Pi) -> Pi-hole's bundled `pihole-FTL sqlite3`
  python (laptop TEST only)              -> stdlib sqlite3 against a gravity.db copy

Usage:
  Production (cron, on the Pi):   python3 apply.py
  Manual test (on the Pi):        sudo python3 apply.py --force-on
                                  sudo python3 apply.py --force-off
  Offline dry-run (laptop):       python3 apply.py --engine python --db gravity-copy.db --dry-run
  Simulate a time:                python3 apply.py --now "2026-07-10 23:30" --dry-run --engine python --db copy.db
  Snooze curfew until morning:    sudo python3 apply.py --snooze
  Cancel a snooze early:          sudo python3 apply.py --resume

Idempotent & self-healing: desired state is recomputed from scratch each run.
"""
import argparse, json, os, re, sqlite3, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE       = Path(__file__).resolve().parent          # .../PiHole-SyncMe/nightBlock
REPO_ROOT  = HERE.parent                               # .../PiHole-SyncMe
TAG        = "[NightCurfew]"
DEFAULT_DB = "/etc/pihole/gravity.db"
REGEX_HINT = re.compile(r"[\^$|?*+()\[\]{}\\]")        # bare . and - are NOT regex
# Persistent snooze marker (fixed path so cron + manual runs agree; override for tests)
SNOOZE_FILE = Path(os.environ.get("NIGHTCURFEW_SNOOZE_FILE",
                                  "/opt/pihole-nightcurfew/snooze_until"))


# ---------------------------------------------------------------------------
# Pure logic (unit-tested on the laptop; no DB, no Pi)
# ---------------------------------------------------------------------------
def parse_lines(text):
    """Return {domain: type}; type 1 = exact deny, 3 = regex deny."""
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            out[line[3:].strip()] = 3
        else:
            out[line] = 3 if REGEX_HINT.search(line) else 1
    return out


def parse_list(path):
    return parse_lines(Path(path).read_text(encoding="utf-8"))


def _hm(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def state_at(cfg, now):
    """True if the curfew should be ON at `now` (a datetime in cfg's tz).
    Overnight window: ON if now >= block OR now < unblock (assumes unblock < block)."""
    if not cfg.get("enabled", True):
        return False
    day = cfg.get("days", {}).get(now.strftime("%A").lower(), {})
    blk, unb = day.get("block"), day.get("unblock")
    if not blk or not unb:
        return False
    mins = now.hour * 60 + now.minute
    return mins >= _hm(blk) or mins < _hm(unb)


def now_in_cfg_tz(cfg, override=None):
    tz = ZoneInfo(cfg.get("timezone", "UTC"))
    if override:
        return datetime.strptime(override, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    return datetime.now(tz)


def next_falling_edge(cfg, now):
    """First datetime > now where the schedule goes ON->OFF (end of the
    current/upcoming block window). Used as the snooze auto-expiry so a snooze
    lasts until the curfew would naturally lift, then normal service resumes."""
    prev = state_at(cfg, now)
    t = now
    for _ in range(8 * 24 * 60):            # scan up to 8 days at 1-min steps
        t += timedelta(minutes=1)
        cur = state_at(cfg, t)
        if prev and not cur:
            return t.replace(second=0, microsecond=0)
        prev = cur
    return now + timedelta(hours=24)        # fallback (e.g. curfew fully disabled)


# --- snooze marker persistence (filesystem) ---
def read_snooze():
    """Return the aware expiry datetime, or None if no/invalid snooze."""
    try:
        return datetime.fromisoformat(SNOOZE_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def write_snooze(expiry):
    SNOOZE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SNOOZE_FILE.write_text(expiry.isoformat())


def clear_snooze():
    try:
        SNOOZE_FILE.unlink()
    except FileNotFoundError:
        pass


def rows_from_json(out):
    """Parse `pihole-FTL sqlite3 -json` output into positional string tuples.
    Robust to any characters in domains/regex; empty result -> []."""
    out = out.strip()
    if not out:
        return []
    return [tuple(str(v) for v in row.values()) for row in json.loads(out)]


# ---------------------------------------------------------------------------
# DB layer - engine 'ftl' (prod) or 'python' (test). Same query API for both.
# ---------------------------------------------------------------------------
class DB:
    def __init__(self, engine, path, dry_run=False):
        self.engine, self.path, self.dry_run = engine, path, dry_run
        if engine == "python":
            self.conn = sqlite3.connect(path, timeout=15)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.conn.execute("PRAGMA busy_timeout = 15000;")
        elif engine != "ftl":
            raise SystemExit(f"unknown engine: {engine}")

    @staticmethod
    def _lit(v):
        return str(v) if isinstance(v, int) else "'" + str(v).replace("'", "''") + "'"

    def _render(self, sql, params):
        parts = sql.split("?")
        if len(parts) - 1 != len(params):
            raise ValueError("placeholder/param count mismatch")
        out = parts[0]
        for p, tail in zip(params, parts[1:]):
            out += self._lit(p) + tail
        return out

    def query(self, sql, params=()):
        """Reads always run (harmless), even in dry-run."""
        if self.engine == "python":
            cur = self.conn.execute(sql, params)
            return [tuple(str(c) for c in row) for row in cur.fetchall()]
        rendered = self._render(sql, params)
        out = subprocess.run(
            ["pihole-FTL", "sqlite3", "-json", self.path, rendered],
            capture_output=True, text=True, check=True).stdout
        return rows_from_json(out)

    def execute(self, sql, params=()):
        if self.dry_run:
            print("  DRY-RUN would exec:", self._render(sql, params))
            return
        if self.engine == "python":
            self.conn.execute(sql, params)
        else:
            subprocess.run(["pihole-FTL", "sqlite3", self.path, self._render(sql, params)],
                           check=True)

    def commit(self):
        if self.engine == "python" and not self.dry_run:
            self.conn.commit()


# ---------------------------------------------------------------------------
# Reconcile + toggle
# ---------------------------------------------------------------------------
def reconcile(db, entries, dry_run):
    """Make the [NightCurfew] rows exactly match `entries`. Returns changed?"""
    rows = db.query("SELECT id, domain, type FROM domainlist WHERE comment = ?;", (TAG,))
    have = {r[1]: (int(r[0]), int(r[2])) for r in rows}
    changed = False

    for dom, typ in entries.items():
        if dom not in have:
            print(f"  + add {'regex' if typ == 3 else 'exact'} deny: {dom}")
            db.execute("INSERT INTO domainlist (type, domain, enabled, comment) "
                       "VALUES (?, ?, 0, ?);", (typ, dom, TAG))
            if not dry_run:
                rid = int(db.query("SELECT id FROM domainlist WHERE domain = ? AND comment = ?;",
                                   (dom, TAG))[0][0])
                db.execute("INSERT OR IGNORE INTO domainlist_by_group (domainlist_id, group_id) "
                           "VALUES (?, 0);", (rid,))  # Default group 0 => all devices
            else:
                print("            -> link to Default group (0)")
            changed = True
        elif have[dom][1] != typ:
            print(f"  ~ retype {dom}: {have[dom][1]} -> {typ}")
            db.execute("UPDATE domainlist SET type = ? WHERE id = ?;", (typ, have[dom][0]))
            changed = True

    for dom, (rid, _) in have.items():
        if dom not in entries:
            print(f"  - remove {dom}")
            db.execute("DELETE FROM domainlist_by_group WHERE domainlist_id = ?;", (rid,))
            db.execute("DELETE FROM domainlist WHERE id = ?;", (rid,))
            changed = True
    return changed


def apply_state(db, on):
    """Set enabled on all [NightCurfew] rows. Returns changed?"""
    val = 1 if on else 0
    n = db.query("SELECT COUNT(*) FROM domainlist WHERE comment = ? AND enabled != ?;", (TAG, val))
    mismatch = int(n[0][0]) if n else 0
    if mismatch:
        print(f"  set enabled={val} on {mismatch} row(s)")
        db.execute("UPDATE domainlist SET enabled = ? WHERE comment = ?;", (val, TAG))
        return True
    return False


def git_pull():
    try:
        subprocess.run(["git", "-C", str(REPO_ROOT), "pull", "--ff-only", "--quiet"],
                       check=True, timeout=60)
    except Exception as e:
        print(f"WARN git pull failed, using cached copy: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="PiHole AutoBlocker reconciler")
    ap.add_argument("--engine", choices=["ftl", "python"], default="ftl",
                    help="ftl = pihole-FTL sqlite3 (production, default); "
                         "python = sqlite3 module (laptop test only)")
    ap.add_argument("--db", default=DEFAULT_DB, help="path to gravity.db (or a copy)")
    ap.add_argument("--dry-run", action="store_true", help="print intended changes, write nothing")
    ap.add_argument("--force-on", action="store_true", help="ignore schedule, force curfew ON")
    ap.add_argument("--force-off", action="store_true", help="ignore schedule, force curfew OFF")
    ap.add_argument("--now", metavar="'YYYY-MM-DD HH:MM'", help="simulate this local time")
    ap.add_argument("--no-pull", action="store_true", help="skip git pull")
    ap.add_argument("--snooze", action="store_true",
                    help="disable the curfew until it would next lift (auto-resumes tomorrow)")
    ap.add_argument("--resume", action="store_true", help="cancel an active snooze now")
    args = ap.parse_args()
    if args.force_on and args.force_off:
        raise SystemExit("--force-on and --force-off are mutually exclusive")
    if args.snooze and args.resume:
        raise SystemExit("--snooze and --resume are mutually exclusive")

    if args.engine == "ftl" and not args.no_pull and not args.dry_run:
        git_pull()

    cfg = json.loads((HERE / "schedule.json").read_text(encoding="utf-8"))
    entries = parse_list(HERE / "nightBlockList.txt")
    now = now_in_cfg_tz(cfg, args.now)

    # --- snooze / resume actions ---
    if args.resume:
        if not args.dry_run:
            clear_snooze()
        print("  snooze cleared - back on the normal schedule")
    if args.snooze:
        expiry = next_falling_edge(cfg, now)
        if not args.dry_run:
            write_snooze(expiry)
        print(f"  snoozed - curfew OFF until {expiry:%a %Y-%m-%d %H:%M %Z}")

    # --- decide desired state ---
    snooze_note = ""
    if args.force_on:
        on = True
    elif args.force_off:
        on = False
    elif args.snooze:
        on = False
    else:
        expiry = read_snooze()
        if expiry and now < expiry:
            on = False
            snooze_note = f" (snoozed until {expiry:%a %H:%M})"
        else:
            if expiry:                       # expired -> auto-resume
                if not args.dry_run:
                    clear_snooze()
                snooze_note = " (snooze expired -> resumed)"
            on = state_at(cfg, now)

    print(f"[{datetime.now().isoformat(timespec='seconds')}] engine={args.engine} "
          f"dry_run={args.dry_run} curfew={'ON' if on else 'OFF'}{snooze_note} "
          f"domains={len(entries)}")

    db = DB(args.engine, args.db, args.dry_run)
    changed = reconcile(db, entries, args.dry_run)
    changed |= apply_state(db, on)
    db.commit()

    if changed:
        if args.engine == "ftl" and not args.dry_run:
            subprocess.run(["pihole", "reloadlists"], check=False)
            print("  ran: pihole reloadlists")
        else:
            print("  (reload skipped - dry-run or python engine)")
    else:
        print("  no change")


if __name__ == "__main__":
    main()
