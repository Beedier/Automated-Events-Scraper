#!/bin/bash
set -euo pipefail

log() { echo -e "\n🔹 $1\n"; }

# DB config (can override with environment variables)
DB_NAME=${DB_NAME:-mydb}
DB_USER=${DB_USER:-user}

# Start containers (only if not running)
if ! podman-compose ps | grep -q "Up"; then
  log "Starting containers..."
  podman-compose up -d
else
  log "Containers already running."
fi

# Restore DB (only if file exists)
if [ -f db_data_backup.sql.gz ]; then
  log "Restoring database..."
  ./restore_data.sh db_data_backup.sql.gz
else
  log "⚠️ Backup file not found, skipping restore."
fi

# Run pipelines
log "Running pipelines..."
for step in \
  "event-url" \
  "process-image" \
  "event-web-content" \
  "generate-content" \
  "upload-media" \
  "create-event" \
  "update-event-category" \
  "update-event"
do
  log "Step: $step"
  uv run main.py "$step" all
done

# Dump DB
log "Dumping database..."
./dump_db.sh

# Commit DB backup only if changed
if git diff --quiet db_data_backup.sql.gz; then
  log "No changes in DB backup, skipping commit."
else
  log "Committing DB backup..."
  git add db_data_backup.sql.gz
  git commit -m "latest db data added."
  git push origin dev

  # Merge to master
  git checkout master
  git merge dev
  git push origin master
  git checkout dev
fi

# Automatically detect the running Postgres container
CONTAINER_ID=$(podman ps --filter "ancestor=postgres" --format "{{.ID}}" | head -n1)
if [ -z "$CONTAINER_ID" ]; then
  log "❌ No running Postgres container found. Skipping report."
else
  log "Using Postgres container: $CONTAINER_ID"

  # Run final DB report
  log "Generating today's event summary..."
  podman exec -i "$CONTAINER_ID" \
    psql -U "$DB_USER" -d "$DB_NAME" -c "
      SELECT website_name, COUNT(*) AS total_events
      FROM events
      WHERE DATE(created_at) = CURRENT_DATE
        AND DATE(updated_at) = CURRENT_DATE
        AND remote_event_id IS NOT NULL
      GROUP BY website_name
      UNION ALL
      SELECT 'total' AS website_name, COUNT(*) AS total_events
      FROM events
      WHERE DATE(created_at) = CURRENT_DATE
        AND DATE(updated_at) = CURRENT_DATE
        AND remote_event_id IS NOT NULL;
    "
fi

# Stop containers
log "Stopping containers..."
podman-compose down

log "✅ Workflow completed successfully."
