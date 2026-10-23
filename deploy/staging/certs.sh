#!/bin/sh
# Throwaway TLS for the staging rehearsal: a CA and a server certificate for the database ("db"), so the application
# connects with ssl_mode=VERIFY_IDENTITY exactly as in production. Never reuse these outside staging.
set -eu
dir="$(dirname "$0")/certs"
mkdir -p "$dir"
cd "$dir"
openssl req -x509 -newkey rsa:2048 -nodes -days 7 -subj "/CN=Syntegra staging CA" -keyout ca-key.pem -out ca.pem 2>/dev/null
openssl req -newkey rsa:2048 -nodes -subj "/CN=db" -keyout server-key.pem -out server.csr 2>/dev/null
printf 'subjectAltName=DNS:db,DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth\n' > san.ext
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -days 7 -extfile san.ext -out server-cert.pem 2>/dev/null
chmod 0644 ca.pem server-cert.pem server-key.pem  # read by mysqld (uid 999) inside its container; staging only
rm -f server.csr san.ext ca.srl
mkdir -p ../backups && chmod 0777 ../backups  # written by the MySQL job (root) and the app image (uid 1001)
echo "staging certificates in $dir"
