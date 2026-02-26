#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting Keycloak database backup..."

# Execute the pg_dump command inside the postgres container
docker exec -t postgres-tskhra pg_dump -U admin keycloak_db > keycloak_backup.sql

echo "Backup completed successfully! Saved to keycloak_backup.sql in the current directory."