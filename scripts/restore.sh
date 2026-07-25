#!/bin/bash
# SyncBridge AI - Disaster Recovery Restore Script

if [ -z "$1" ]; then
    echo "Usage: ./scripts/restore.sh <path_to_sql_dump>"
    exit 1
fi

SQL_FILE=$1

if [ ! -f "$SQL_FILE" ]; then
    echo "Error: File $SQL_FILE does not exist."
    exit 1
fi

echo "Restoring SyncBridge Database from $SQL_FILE..."

mysql -u syncuser -psyncpass -h 127.0.0.1 syncbridgedb < "$SQL_FILE"

echo "Database restore completed successfully."
