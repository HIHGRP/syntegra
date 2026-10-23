#!/bin/sh
# Dump every Syntegra zone over TLS (ssl-mode VERIFY_IDENTITY) with the read-only backup account (CR-008 staging).
# Masking is done by the application, never by MySQL masking policies, so none are dumped.
set -eu
mkdir -p /backups/db
for z in django platform registry ops vault records dw; do
  mysqldump --host=db --user=backup --password=staging-backup-password \
    --ssl-mode=VERIFY_IDENTITY --ssl-ca=/certs/ca.pem \
    --single-transaction --routines --triggers --events --hex-blob --no-tablespaces --set-gtid-purged=OFF --skip-masking-policies \
    --databases "syn_stg_$z" > "/backups/db/syn_stg_$z.sql"
  echo "dumped syn_stg_$z: $(wc -c < "/backups/db/syn_stg_$z.sql") bytes"
done
