#!/bin/bash

# --- Configuration ---
SERVER="your_username@your_server_ip"
PROJECT_DIR="$HOME/Projects/TskhraApplication"

echo "🚀 Starting deployment to $SERVER..."

# Connect via SSH and run the block of commands below
# shellcheck disable=SC2087
ssh $SERVER "bash -s" << EOF
  # 'set -e' makes the script stop immediately if any command fails (e.g., if Maven fails, Docker won't build)
  set -e

  echo "📦 Pulling latest code from Git..."
  cd $PROJECT_DIR
  git pull

  echo "☕ Building Maven project..."
  cd Modulith/
  mvn clean package

  echo "🐳 Rebuilding and starting Docker container..."
  cd ..
  docker compose up -d --build modulith

  echo "✅ Deployment successful!"
EOF