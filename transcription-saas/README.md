# VoiceScript AI - Voice Transcription SaaS

A complete AI-powered voice transcription Software-as-a-Service (SaaS) platform built with FastAPI, React, and OpenAI Whisper.

## 🚀 Features

- **AI-Powered Transcription**: Uses OpenAI Whisper for highly accurate voice-to-text conversion
- **Modern Web Interface**: Beautiful, responsive React frontend with Tailwind CSS
- **User Authentication**: Secure JWT-based authentication system
- **API Key Management**: Generate and manage API keys for programmatic access
- **Subscription Management**: Integrated Stripe billing for SaaS monetization
- **File Upload**: Drag-and-drop interface supporting multiple audio formats
- **Transcription History**: View, search, and manage all your transcriptions
- **Real-time Processing**: Fast transcription with progress indicators
- **RESTful API**: Complete API for integration with other applications
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Production Ready**: Includes SSL, rate limiting, and security headers

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **OpenAI Whisper** - AI transcription service
- **Stripe** - Payment processing
- **JWT** - Authentication
- **SQLite** - Database (easily replaceable with PostgreSQL)

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Dropzone** - File upload component

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **Docker Compose** - Multi-container orchestration

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Stripe account (for payments)
- Domain name (for production)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd transcription-saas
./scripts/setup.sh
```

### 2. Configure Environment

Edit the `.env` file with your API keys:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Database Configuration
DATABASE_URL=sqlite:///./transcription_saas.db
```

### 3. Start Development Server

```bash
./scripts/start.sh
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🌐 Production Deployment

### 1. Prepare Server

```bash
# On your production server
git clone <repository-url>
cd transcription-saas
```

### 2. Configure SSL

Add your SSL certificates to the `ssl/` directory:
- `ssl/cert.pem` - SSL certificate
- `ssl/key.pem` - SSL private key

### 3. Deploy

```bash
sudo ./scripts/deploy.sh
```

This will:
- Install Docker if needed
- Build and start production services
- Configure firewall rules
- Setup automated backups
- Configure log rotation

## 📊 API Documentation

### Authentication

All API endpoints require authentication via Bearer token:

```bash
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login

#### Transcription
- `POST /transcribe` - Upload and transcribe audio file
- `GET /transcriptions` - Get user's transcriptions

#### API Keys
- `POST /api-keys` - Create new API key
- `GET /api-keys` - List user's API keys

#### Subscriptions
- `POST /subscriptions/create-checkout` - Create Stripe checkout session
- `GET /subscriptions/current` - Get current subscription
- `POST /subscriptions/cancel` - Cancel subscription

### Example Usage

```bash
# Upload audio file for transcription
curl -X POST "http://localhost:8000/transcribe" \
  -H "Authorization: Bearer <token>" \
  -F "file=@audio.mp3"

# Get transcription history
curl -X GET "http://localhost:8000/transcriptions" \
  -H "Authorization: Bearer <token>"
```

## 💳 Subscription Plans

The platform includes three subscription tiers:

- **Starter** (Free): 60 minutes/month
- **Professional** ($29/month): 500 minutes/month + API access
- **Enterprise** ($99/month): Unlimited minutes + priority support

## 🔧 Management Scripts

### Backup and Restore

```bash
# Create backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backups/transcription-saas-backup-YYYYMMDD_HHMMSS.tar.gz
```

### Monitoring

```bash
# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Restart services
docker-compose restart
```

## 🔒 Security Features

- JWT-based authentication
- Rate limiting on API endpoints
- CORS protection
- SQL injection prevention
- XSS protection headers
- SSL/TLS encryption (production)
- Secure file upload validation

## 📁 Project Structure

```
transcription-saas/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # Authentication logic
│   ├── payment.py          # Stripe integration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── contexts/       # React contexts
│   └── package.json        # Node dependencies
├── docker/                 # Docker configuration
│   ├── Dockerfile.backend  # Backend container
│   ├── Dockerfile.frontend # Frontend container
│   └── nginx.conf          # Nginx configuration
├── scripts/                # Management scripts
│   ├── setup.sh           # Initial setup
│   ├── start.sh           # Development start
│   ├── deploy.sh          # Production deployment
│   ├── backup.sh          # Backup script
│   └── restore.sh         # Restore script
└── docker-compose.yml      # Service orchestration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs with `docker-compose logs`
- Open an issue on GitHub

## 🔄 Updates

To update the application:

```bash
git pull
./scripts/deploy.sh  # For production
# or
./scripts/start.sh   # For development
```

## 🎯 Roadmap

- [ ] Multi-language transcription support
- [ ] Real-time transcription via WebSocket
- [ ] Advanced audio processing options
- [ ] Team collaboration features
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Custom vocabulary training
- [ ] Batch processing capabilities

---

Built with ❤️ using FastAPI, React, and OpenAI Whisper