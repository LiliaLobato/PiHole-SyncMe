#!/usr/bin/env bash
# PiHole AutoBlocker - one-time Pi setup. Does NOT enable cron (test first!).
set -euo pipefail

BASE=/opt/pihole-nightcurfew
REPO="$BASE/PiHole-SyncMe"
GIT_URL="https://github.com/LiliaLobato/PiHole-SyncMe.git"

echo "==> creating $BASE"
sudo mkdir -p "$BASE"

if [ ! -d "$REPO/.git" ]; then
  echo "==> cloning repo"
  sudo git clone "$GIT_URL" "$REPO"
else
  echo "==> repo already present, pulling"
  sudo git -C "$REPO" pull --ff-only
fi
sudo git config --global --add safe.directory "$REPO"

echo "==> backing up gravity.db (consistent copy via .backup)"
sudo pihole-FTL sqlite3 /etc/pihole/gravity.db ".backup /etc/pihole/gravity.db.bak-$(date +%F)"

cat <<EOF

Done. NOTHING scheduled yet. Test manually first:

  # BLOCK now, then from the laptop:  nslookup www.instagram.com 10.0.0.174  (expect 0.0.0.0)
  sudo python3 $REPO/nightBlock/apply.py --force-on

  # UNBLOCK now, then from the laptop: nslookup www.instagram.com 10.0.0.174  (expect real IP)
  sudo python3 $REPO/nightBlock/apply.py --force-off

When happy, enable the schedule (every 10 min):

  echo '*/10 * * * * root /usr/bin/python3 $REPO/nightBlock/apply.py >> /var/log/pihole-nightcurfew.log 2>&1' \\
    | sudo tee /etc/cron.d/pihole-nightcurfew >/dev/null
  sudo chmod 644 /etc/cron.d/pihole-nightcurfew
EOF
