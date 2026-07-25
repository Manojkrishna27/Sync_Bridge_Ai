#!/bin/bash
# SyncBridge AI - MySQL & Redis Disaster Recovery Backup Script

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR

echo "Starting SyncBridge Backup [$TIMESTAMP]..."

# 1. MySQL Dump Backup
if command -v mysqldump &> /dev/null; then
    mysqldump -u syncuser -psyncpass -h 127.0.0.1 syncbridgedb > "$BACKUP_DIR/mysql_backup_$TIMESTAMP.sql"
    echo "MySQL Backup saved to $BACKUP_DIR/mysql_backup_$TIMESTAMP.sql"
else
    echo "Warning: mysqldump command not found. Skipping SQL backup."
fi

# 2. Redis RDB Snapshot Backup
if command -v redis-cli &> /dev/null; then
    redis-cli BGSAVE
    echo "Redis BGSAVE snapshot initiated."
fi

echo "Backup completed successfully."
