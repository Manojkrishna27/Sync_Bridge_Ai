#!/bin/sh
# Ensure the SQLite database file is writable by syncuser
DB_FILE="/app/syncbridge_local.db"

if [ -f "$DB_FILE" ]; then
    chmod 666 "$DB_FILE"
fi

# Execute the container's main command as syncuser
exec "$@"
