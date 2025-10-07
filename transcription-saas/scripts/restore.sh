#!/bin/bash

# VoiceScript AI - Restore Script
echo "🔄 Restoring VoiceScript AI from backup..."

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -la backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Confirm restore
echo "⚠️  This will overwrite existing data!"
read -p "Are you sure you want to restore from $BACKUP_FILE? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Stop services
echo "🛑 Stopping services..."
docker-compose down

# Create temporary restore directory
TEMP_DIR="/tmp/restore-$(date +%s)"
mkdir -p $TEMP_DIR

# Extract backup
echo "📦 Extracting backup..."
tar -xzf "$BACKUP_FILE" -C $TEMP_DIR

# Find the backup directory
BACKUP_DIR=$(find $TEMP_DIR -name "transcription-saas-backup-*" -type d | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ Invalid backup file format"
    rm -rf $TEMP_DIR
    exit 1
fi

# Restore database
echo "📊 Restoring database..."
mkdir -p database
if [ -f "$BACKUP_DIR/database.db" ]; then
    cp "$BACKUP_DIR/database.db" database/transcription_saas.db
    echo "✅ Database restored"
else
    echo "⚠️  No database found in backup"
fi

# Restore uploads
echo "📁 Restoring uploads..."
if [ -d "$BACKUP_DIR/uploads" ]; then
    rm -rf uploads
    cp -r "$BACKUP_DIR/uploads" .
    echo "✅ Uploads restored"
else
    echo "⚠️  No uploads found in backup"
fi

# Restore configuration (with confirmation)
if [ -f "$BACKUP_DIR/.env" ]; then
    read -p "Restore .env configuration? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$BACKUP_DIR/.env" .
        echo "✅ Configuration restored"
    fi
fi

if [ -f "$BACKUP_DIR/frontend.env" ]; then
    read -p "Restore frontend configuration? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$BACKUP_DIR/frontend.env" frontend/.env
        echo "✅ Frontend configuration restored"
    fi
fi

# Cleanup temporary directory
rm -rf $TEMP_DIR

# Start services
echo "🚀 Starting services..."
docker-compose up -d

echo "✅ Restore completed successfully!"
echo "🌐 Application should be available at http://localhost:3000"