#!/bin/bash

# VoiceScript AI - Production Deployment Script
echo "🚀 Deploying VoiceScript AI to production..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root for production deployment"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./scripts/setup.sh first."
    exit 1
fi

# Check SSL certificates
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo "⚠️  SSL certificates not found in ssl/ directory"
    echo "Please add your SSL certificates:"
    echo "  ssl/cert.pem - SSL certificate"
    echo "  ssl/key.pem - SSL private key"
    echo ""
    read -p "Continue without SSL? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Set production environment
export COMPOSE_PROFILES=production

# Build and start production services
echo "🔨 Building and starting production services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Setup firewall rules
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Setup log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/transcription-saas << EOF
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 root root
    postrotate
        docker kill --signal="USR1" \$(docker ps -q) 2>/dev/null || true
    endscript
}
EOF

# Setup backup script
echo "💾 Setting up backup script..."
cat > /usr/local/bin/backup-transcription-saas.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/transcription-saas"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T backend cp /app/transcription_saas.db /tmp/backup.db
docker cp transcription-backend:/tmp/backup.db $BACKUP_DIR/database_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/backup-transcription-saas.sh

# Setup daily backup cron job
echo "0 2 * * * /usr/local/bin/backup-transcription-saas.sh" | crontab -

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Production deployment successful!"
    echo ""
    echo "🌐 Your application is now running at:"
    echo "   https://your-domain.com"
    echo ""
    echo "📊 To monitor services:"
    echo "   docker-compose logs -f"
    echo ""
    echo "💾 Backups are scheduled daily at 2 AM"
    echo "   Manual backup: /usr/local/bin/backup-transcription-saas.sh"
    echo ""
    echo "🔧 To update the application:"
    echo "   git pull && ./scripts/deploy.sh"
else
    echo "❌ Deployment failed. Check logs with: docker-compose logs"
    exit 1
fi