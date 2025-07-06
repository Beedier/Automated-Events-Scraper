#!/bin/bash

# Config
DB_SERVICE_NAME="db"
DB_NAME="mydb"
DB_USER="user"
DATA_FILE="$1"

# Usage check
if [ -z "$DATA_FILE" ]; then
  echo "Usage: $0 path_to_data_sql_file"
  exit 1
fi

if [ ! -f "$DATA_FILE" ]; then
  echo "❌ File not found: $DATA_FILE"
  exit 2
fi

CONTAINER_ID=$(podman ps --filter "name=${DB_SERVICE_NAME}" --format "{{.ID}}" | head -n 1)

if [ -z "$CONTAINER_ID" ]; then
  echo "❌ Database container ($DB_SERVICE_NAME) not running."
  exit 3
fi

echo "🧹 Discovering tables to truncate..."

# Get all table names except alembic_version
TABLES=$(podman exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
  "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename != 'alembic_version';" | tr -d ' ')

if [ -z "$TABLES" ]; then
  echo "⚠️ No tables found to truncate."
else
  for table in $TABLES; do
    echo "🔁 Truncating $table..."
    podman exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME" -c "TRUNCATE TABLE $table RESTART IDENTITY CASCADE;"
  done
fi

echo "📥 Restoring data from $DATA_FILE ..."

if podman exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME" < "$DATA_FILE"; then
  echo "✅ Restore completed. Please check output above for any row-level errors."
else
  echo "❌ Restore failed. See error messages above."
  exit 4
fi
