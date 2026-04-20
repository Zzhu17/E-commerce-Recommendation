#!/usr/bin/env bash
set -euo pipefail

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DRILL_DB="${DRILL_DB:-${POSTGRES_DB}_restore_drill}"
HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5434}"

mkdir -p "${BACKUP_DIR}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RAW="${BACKUP_DIR}/${POSTGRES_DB}_${STAMP}.dump"
ENC="${RAW}.enc"
TMP_RESTORE="${BACKUP_DIR}/${POSTGRES_DB}_${STAMP}_drill.dump"

export PGPASSWORD="${POSTGRES_PASSWORD}"

T0="$(date +%s)"
pg_dump -h "${HOST}" -p "${PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -F c -f "${RAW}"
T1="$(date +%s)"

openssl enc -aes-256-cbc -pbkdf2 -salt -in "${RAW}" -out "${ENC}" -pass env:BACKUP_ENCRYPTION_PASSPHRASE
rm -f "${RAW}"
openssl enc -d -aes-256-cbc -pbkdf2 -in "${ENC}" -out "${TMP_RESTORE}" -pass env:BACKUP_ENCRYPTION_PASSPHRASE

dropdb --if-exists -h "${HOST}" -p "${PORT}" -U "${POSTGRES_USER}" "${DRILL_DB}"
createdb -h "${HOST}" -p "${PORT}" -U "${POSTGRES_USER}" "${DRILL_DB}"
pg_restore -h "${HOST}" -p "${PORT}" -U "${POSTGRES_USER}" -d "${DRILL_DB}" "${TMP_RESTORE}"
T2="$(date +%s)"

cat <<METRICS
backup_file=${ENC}
rpo_seconds=$((T1 - T0))
rto_seconds=$((T2 - T1))
restore_drill_db=${DRILL_DB}
METRICS

rm -f "${TMP_RESTORE}"
