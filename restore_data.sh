#!/bin/bash

# Config
DB_SERVICE_NAME="db"
DB_NAME="mydb"
DB_USER="user"
DATA_FILE="$1"

# Usage check
if [ -z "$DATA_FILE" ]; then
  echo "Usage: $0 path_to_data_sql_file(.sql or .sql.gz)"
  exit 1
fi

if [ ! -f "$DATA_FILE" ]; then
  echo "❌ File not found: $DATA_FILE"
  exit 2
fi

CONTAINER_ID=$(docker ps --filter "name=${DB_SERVICE_NAME}" --format "{{.ID}}" | head -n 1)

if [ -z "$CONTAINER_ID" ]; then
  echo "❌ Database container ($DB_SERVICE_NAME) not running."
  exit 3
fi

echo "🧹 Discovering tables to truncate..."

TABLES=$(docker exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
  "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename != 'alembic_version';" | tr -d ' ')

if [ -z "$TABLES" ]; then
  echo "⚠️ No tables found to truncate."
else
  for table in $TABLES; do
    echo "🔁 Truncating $table..."
    docker exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME" -c "TRUNCATE TABLE $table RESTART IDENTITY CASCADE;"
  done
fi

echo "📥 Restoring data from $DATA_FILE ..."

# Detect gzipped file and decompress on-the-fly
if [[ "$DATA_FILE" == *.gz ]]; then
  if gunzip -c "$DATA_FILE" | docker exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME"; then
    echo "✅ Restore completed from compressed file."
  else
    echo "❌ Restore failed from compressed file."
    exit 4
  fi
else
  if docker exec -i "$CONTAINER_ID" psql -U "$DB_USER" -d "$DB_NAME" < "$DATA_FILE"; then
    echo "✅ Restore completed from SQL file."
  else
    echo "❌ Restore failed from SQL file."
    exit 4
  fi
fi
