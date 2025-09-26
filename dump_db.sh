#!/bin/bash

# Configuration
DB_SERVICE_NAME="db"
DB_NAME="mydb"
DB_USER="user"
OUTPUT_DIR="."
OUTPUT_FILE="$OUTPUT_DIR/db_data_backup.sql.gz"

# Get container ID of the db service
CONTAINER_ID=$(podman ps --filter "name=${DB_SERVICE_NAME}" --format "{{.ID}}" | head -n 1)

if [ -z "$CONTAINER_ID" ]; then
  echo "❌ Database container ($DB_SERVICE_NAME) not running."
  exit 1
fi

echo "📦 Creating compressed data-only database dump..."

# Dump and compress
if podman exec "$CONTAINER_ID" pg_dump --data-only -U "$DB_USER" "$DB_NAME" --exclude-table=alembic_version | gzip > "$OUTPUT_FILE"; then
  echo "✅ Compressed data-only database dump successful: $OUTPUT_FILE"
else
  echo "❌ Compressed data-only database dump failed."
  exit 2
fi
