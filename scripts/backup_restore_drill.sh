#!/usr/bin/env bash
set -euo pipefail

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DRILL_DB="${DRILL_DB:-${POSTGRES_DB}_restore_drill}"
ENCRYPTION_PASSPHRASE="${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"

mkdir -p "${BACKUP_DIR}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PLAIN_BACKUP="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"
ENCRYPTED_BACKUP="${PLAIN_BACKUP}.enc"

export PGPASSWORD="${POSTGRES_PASSWORD}"

START_EPOCH="$(date +%s)"
pg_dump -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5434}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -F c -f "${PLAIN_BACKUP}"
BACKUP_DONE_EPOCH="$(date +%s)"

openssl enc -aes-256-cbc -pbkdf2 -salt -in "${PLAIN_BACKUP}" -out "${ENCRYPTED_BACKUP}" -pass env:ENCRYPTION_PASSPHRASE
rm -f "${PLAIN_BACKUP}"

DECRYPTED_BACKUP="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}_drill.dump"
openssl enc -d -aes-256-cbc -pbkdf2 -in "${ENCRYPTED_BACKUP}" -out "${DECRYPTED_BACKUP}" -pass env:ENCRYPTION_PASSPHRASE

dropdb --if-exists -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5434}" -U "${POSTGRES_USER}" "${DRILL_DB}"
createdb -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5434}" -U "${POSTGRES_USER}" "${DRILL_DB}"
pg_restore -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5434}" -U "${POSTGRES_USER}" -d "${DRILL_DB}" "${DECRYPTED_BACKUP}"
RESTORE_DONE_EPOCH="$(date +%s)"

RPO_SECONDS=$((BACKUP_DONE_EPOCH - START_EPOCH))
RTO_SECONDS=$((RESTORE_DONE_EPOCH - BACKUP_DONE_EPOCH))

cat <<METRICS
backup_file=${ENCRYPTED_BACKUP}
rpo_seconds=${RPO_SECONDS}
rto_seconds=${RTO_SECONDS}
restore_drill_db=${DRILL_DB}
METRICS

rm -f "${DECRYPTED_BACKUP}"
