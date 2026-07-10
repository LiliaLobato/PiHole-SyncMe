#!/usr/bin/env python3
"""Laptop unit tests for the PURE logic in apply.py (no DB, no Pi).
Run:  python test_schedule.py
Covers the overnight-window schedule math and list parsing - where real bugs live."""
from datetime import datetime
from zoneinfo import ZoneInfo
from apply import state_at, parse_lines

TZ = ZoneInfo("America/Los_Angeles")
CFG = {
    "enabled": True,
    "timezone": "America/Los_Angeles",
    "days": {
        "monday":    {"block": "22:00", "unblock": "07:00"},
        "tuesday":   {"block": "22:00", "unblock": "07:00"},
        "wednesday": {"block": "22:00", "unblock": "07:00"},
        "thursday":  {"block": "22:00", "unblock": "07:00"},
        "friday":    {"block": "23:00", "unblock": "08:00"},
        "saturday":  {"block": "23:00", "unblock": "08:00"},
        "sunday":    {"block": "22:00", "unblock": "07:00"},
    },
}

fails = 0
def dt(y, mo, d, h, mi):
    return datetime(y, mo, d, h, mi, tzinfo=TZ)

def check(name, got, want):
    global fails
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got}, want {want}")
    fails += (0 if ok else 1)

# --- schedule math (2026-07-06 is Monday, 07-10 Friday, 07-11 Saturday) ---
check("Mon 21:59 -> OFF",                 state_at(CFG, dt(2026,7,6,21,59)), False)
check("Mon 22:00 -> ON (block edge)",     state_at(CFG, dt(2026,7,6,22,0)),  True)
check("Tue 03:00 -> ON (overnight)",      state_at(CFG, dt(2026,7,7,3,0)),   True)
check("Tue 06:59 -> ON",                  state_at(CFG, dt(2026,7,7,6,59)),  True)
check("Tue 07:00 -> OFF (unblock edge)",  state_at(CFG, dt(2026,7,7,7,0)),   False)
check("Tue 12:00 -> OFF (daytime)",       state_at(CFG, dt(2026,7,7,12,0)),  False)
check("Fri 22:30 -> OFF (per-day 23:00)", state_at(CFG, dt(2026,7,10,22,30)),False)
check("Fri 23:00 -> ON",                  state_at(CFG, dt(2026,7,10,23,0)), True)
check("Sat 07:30 -> ON (per-day 08:00)",  state_at(CFG, dt(2026,7,11,7,30)), True)
check("Sat 08:00 -> OFF",                 state_at(CFG, dt(2026,7,11,8,0)),  False)

# --- null night = OFF all day ---
NCFG = {**CFG, "days": {**CFG["days"], "wednesday": {"block": None, "unblock": None}}}
check("Wed null 23:00 -> OFF",            state_at(NCFG, dt(2026,7,8,23,0)), False)

# --- global kill switch ---
check("enabled=false -> OFF",             state_at({**CFG, "enabled": False}, dt(2026,7,6,23,0)), False)

# --- list parsing ---
p = parse_lines("# comment\nwww.reddit.com\n(\\.|^)tiktok\\.com$\nre:foo\\.bar\n\n")
check("exact deny (type 1)",  p.get("www.reddit.com"),        1)
check("regex deny (type 3)",  p.get("(\\.|^)tiktok\\.com$"),  3)
check("re: prefix forces regex", p.get("foo\\.bar"),          3)
check("comments/blanks ignored", len(p),                      3)

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' TEST(S) FAILED'}")
raise SystemExit(1 if fails else 0)
