#!/bin/bash
set -euo pipefail

log() {
  echo -e "\n🔹 $1\n"
}

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

# Stop containers
log "Stopping containers..."
podman-compose down

log "✅ Workflow completed successfully."
