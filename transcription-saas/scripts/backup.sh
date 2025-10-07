#!/bin/bash

# VoiceScript AI - Backup Script
echo "💾 Creating backup of VoiceScript AI..."

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="transcription-saas-backup-$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create temporary backup directory
TEMP_DIR="/tmp/$BACKUP_NAME"
mkdir -p $TEMP_DIR

# Backup database
echo "📊 Backing up database..."
if docker-compose ps | grep -q "backend.*Up"; then
    docker-compose exec -T backend cp /app/transcription_saas.db /tmp/backup.db
    docker cp transcription-backend:/tmp/backup.db $TEMP_DIR/database.db
else
    cp database/transcription_saas.db $TEMP_DIR/database.db 2>/dev/null || echo "⚠️  Database file not found"
fi

# Backup uploads
echo "📁 Backing up uploads..."
if [ -d "uploads" ]; then
    cp -r uploads $TEMP_DIR/
else
    echo "⚠️  Uploads directory not found"
fi

# Backup configuration
echo "⚙️  Backing up configuration..."
cp .env $TEMP_DIR/ 2>/dev/null || echo "⚠️  .env file not found"
cp frontend/.env $TEMP_DIR/frontend.env 2>/dev/null || echo "⚠️  Frontend .env file not found"

# Create backup archive
echo "📦 Creating backup archive..."
cd /tmp
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" $BACKUP_NAME/

# Cleanup temporary directory
rm -rf $TEMP_DIR

# Remove old backups (keep last 10)
echo "🧹 Cleaning up old backups..."
cd - > /dev/null
ls -t $BACKUP_DIR/*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null

echo "✅ Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "📊 Backup size: $(du -h $BACKUP_DIR/$BACKUP_NAME.tar.gz | cut -f1)"