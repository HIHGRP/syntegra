#!/bin/sh
# Restore every dump into the empty restore server (CR-008 staging).
set -eu
for f in /backups/db/*.sql; do
  mysql --host=db-restore --user=root --password=restore-root-password < "$f"
  echo "restored $(basename "$f")"
done
