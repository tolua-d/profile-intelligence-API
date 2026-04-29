# Insighta Labs+ Platform - Complete Implementation Guide

## Overview

Insighta Labs+ is a comprehensive Platform for Profile Intelligence with three main components:

1. **Backend API** - Django REST API with GitHub OAuth, RBAC, and profile management
2. **CLI Tool** - Command-line interface for profile operations
3. **Web Portal** - React/Next.js web application for visual profile management

All three share the same API backend, ensuring consistency across interfaces.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub OAuth                          │
│         (PKCE flow for security)                        │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌─────────┐
    │ CLI    │ │ Web    │ │ Mobile  │
    │ Tool   │ │ Portal │ │ (Future)│
    └────────┘ └────────┘ └─────────┘
        │          │          │
        └──────────┼──────────┘
                   │
        ┌──────────▼──────────┐
        │  Django REST API    │
        │  - JWT Tokens       │
        │  - RBAC             │
        │  - Rate Limiting    │
        │  - Logging          │
        └─────────┬───────────┘
                  │
        ┌─────────▼──────────┐
        │   PostgreSQL       │
        │   Database         │
        └────────────────────┘
```

## API Versioning

The API supports multiple versions for backward compatibility:

### v1 - Legacy (Maintenance Only)
```
GET /api/v1/profiles
POST /api/v1/profiles
GET /api/v1/profiles/{id}
```

### v2 - Current (Recommended)
```
GET /api/v2/profiles
POST /api/v2/profiles
GET /api/v2/profiles/{id}
DELETE /api/v2/profiles/{id}
GET /api/v2/profiles/search?q=...
GET /api/v2/profiles/export/csv
```

Version is specified in URL path. Response format includes version metadata.

## Authentication Flow

### OAuth with PKCE (Recommended for Web)

```
1. User clicks "Sign in with GitHub"
2. App generates PKCE code_verifier and code_challenge
3. Redirects to: 
   https://github.com/login/oauth/authorize?
     client_id=...&
     redirect_uri=...&
     scope=user&
     code_challenge=...&
     code_challenge_method=S256

4. User authorizes
5. GitHub redirects to: http://app.com/callback?code=...
6. App exchanges code + code_verifier for tokens:
   POST /auth/github/token/ {code, code_verifier}
   
7. Backend returns:
   {
     "access": "eyJ...",
     "refresh": "eyJ...",
     "user": {...}
   }

8. Tokens stored in HTTP-only cookies (web) or credentials.json (CLI)
```

### Token Management

- **Access Token**: 10 minute expiry
- **Refresh Token**: 7 day expiry
- **Automatic Refresh**: Clients automatically refresh on 401
- **Token Blacklist**: Logout adds token to blacklist

## Implementation Status

### ✅ Completed

- [x] GitHub OAuth with PKCE (backend)
- [x] JWT token management (access + refresh)
- [x] Role-based access control (admin, analyst)
- [x] API versioning (v1, v2)
- [x] Enhanced pagination with metadata
- [x] CSV profile export
- [x] Rate limiting middleware
- [x] Request logging middleware
- [x] CSRF protection configuration
- [x] HTTP-only cookie support
- [x] CLI tool with credential storage
- [x] Natural language search (Stage 2)
- [x] Filtering, sorting, pagination (Stage 2)
- [x] Profile creation from external APIs

### 🔄 In Progress

- [ ] Web portal frontend (separate repo)
- [ ] Comprehensive testing suite
- [ ] API documentation (detailed endpoint specs)

### 📋 Planned

- [ ] Admin dashboard for user management
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics and reporting
- [ ] Batch profile operations
- [ ] Webhooks for notifications
- [ ] Advanced search with saved queries

## Installation & Setup

### Backend Setup

1. **Clone repository**
   ```bash
   git clone <backend-repo>
   cd profile-intelligence-API
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=False
   DATABASE_URL=postgresql://user:pass@localhost/insighta
   
   # GitHub OAuth
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback/
   FRONTEND_URL=http://localhost:3000

   # CORS 
   ALLOWED_HOSTS=localhost,127.0.0.1,.insighta.io
   RATELIMIT_ENABLE=True
   CORS_ALLOWED_ORIGINS=http://localhost:3000,https://insighta.io

   # DB
   POSTGRES_USER=insighta
   POSTGRES_PASSWORD=insighta_password
   POSTGRES_DB=insighta
   REDIS_PORT=6379
   API_PORT=8000
   DB_PORT=5432

   # Session
   SESSION_COOKIE_SECURE = False
   SESSION_COOKIE_HTTPONLY = True
   SESSION_COOKIE_SAMESITE = 'Lax'  
   CORS_ALLOW_CREDENTIALS = True
   CORS_ALLOW_CREDENTIALS = True
   CORS_ALLOWED_ORIGINS = http://localhost:3000"
   SESSION_COOKIE_AGE=3600
   CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000

   
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run server**
   ```bash
   python manage.py runserver
   ```

### CLI Tool Setup

1. **Install from source**
   ```bash
   cd cli
   pip install -e .
   ```

2. **Or install from PyPI** (when published)
   ```bash
   pip install insighta-cli
   ```

3. **Verify installation**
   ```bash
   insighta --version
   ```

4. **Login**
   ```bash
   insighta login
   ```

### Web Portal Setup

See [WEB_PORTAL_SETUP.md](./WEB_PORTAL_SETUP.md) for detailed web portal setup instructions.

## API Endpoints

### Authentication

```
POST   /auth/github/login          # Initiate GitHub OAuth
GET    /auth/github/callback       # GitHub OAuth callback
POST   /auth/github/token/         # Exchange code for tokens (CLI)
POST   /auth/token/refresh/        # Refresh access token
POST   /auth/logout/               # Logout and blacklist token
GET    /auth/me/                   # Get current user info
```

### Profiles (v2)

```
GET    /api/v2/profiles                    # List profiles (paginated)
POST   /api/v2/profiles                    # Create profile
GET    /api/v2/profiles/{id}               # Get profile details
DELETE /api/v2/profiles/{id}               # Delete profile (admin/analyst)
GET    /api/v2/profiles/search?q=...       # Search with natural language
GET    /api/v2/profiles/export/csv         # Export as CSV (analyst+)
```

### Filtering & Searching

**List Filters**
```
GET /api/v2/profiles?
  page=1&
  limit=10&
  gender=male&
  age_group=adult&
  country_id=NG&
  min_age=18&
  max_age=65&
  min_gender_probability=0.8&
  min_country_probability=0.5&
  sort_by=age&
  order_by=desc
```

**Natural Language Search**
```
GET /api/v2/profiles/search?q=female+adults+from+Nigeria
GET /api/v2/profiles/search?q=males+older+than+25
GET /api/v2/profiles/search?q=children+from+age+5+to+12
```

## Request/Response Format

### v2 Response Format (Success)

```json
{
  "status": "success",
  "version": "v2",
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 42,
    "pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "data": [
    {
      "id": "019db06d-b517-70dd-8746-8c1e039a8dc0",
      "name": "Thabo Ndebele",
      "gender": "male",
      "gender_probability": 0.66,
      "age": 18,
      "age_group": "teenager",
      "country_id": "AO",
      "country_name": "Angola",
      "country_probability": 0.68,
      "created_at": "2026-04-21T14:24:32.183559Z"
    }
  ]
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Unauthorized",
  "code": "UNAUTHORIZED"
}
```

## Role-Based Access Control

### Admin Role
- Full access to all endpoints
- Can manage users and permissions
- Can view all audit logs
- Full export capabilities

### Analyst Role
- Create and view profiles
- Search and filter profiles
- Export profiles to CSV
- Cannot delete profiles (admin only)
- Cannot manage users

### Permissions by Endpoint

```
POST   /api/v2/profiles           Authenticated users
GET    /api/v2/profiles           Authenticated users
GET    /api/v2/profiles/{id}      Authenticated users
DELETE /api/v2/profiles/{id}      Admin only
GET    /api/v2/profiles/export    Analyst+ only
POST   /auth/logout/              Authenticated users
```

## Rate Limiting

- **Limit**: 100 requests per hour per IP
- **Headers**:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 99
  - `X-RateLimit-Reset`: Unix timestamp

Response on limit exceeded:
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

## Security Features

### ✅ Implemented

1. **HTTPS/TLS**: Secure communication in production
2. **PKCE OAuth Flow**: Secure OAuth for SPAs
3. **HTTP-Only Cookies**: Prevents XSS token theft
4. **CSRF Protection**: Token validation for state changes
5. **SameSite Cookies**: Protects against CSRF attacks
6. **Password Hashing**: Using Django's built-in hash algorithm
7. **Token Blacklist**: Logout invalidates tokens
8. **Role-Based Access**: Fine-grained permissions
9. **Rate Limiting**: DDoS protection
10. **Request Logging**: Audit trail

### 🔒 Best Practices

1. **Never commit secrets**: Use environment variables
2. **Keep dependencies updated**: Run `pip list --outdated`
3. **Use HTTPS in production**: Enforce secure cookies
4. **Rotate secrets regularly**: Keys and tokens
5. **Monitor logs**: Watch for suspicious activity
6. **Test permissions**: Ensure RBAC works correctly

## Deployment

### Environment Variables

Create `.env` for production:

```env
# Django
SECRET_KEY=very-secret-key
DEBUG=False
ALLOWED_HOSTS=insighta.io,www.insighta.io

# Database
DATABASE_URL=postgresql://user:pass@db.host/insighta

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# OAuth
GITHUB_CLIENT_ID=prod-client-id
GITHUB_CLIENT_SECRET=prod-client-secret
GITHUB_REDIRECT_URI=https://insighta.io/auth/github/callback/
FRONTEND_URL=https://app.insighta.io

# Logging
LOG_LEVEL=INFO
```

### Docker Deployment

```bash
docker-compose up -d
```

See `docker-compose.yml` for full configuration.

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create insighta-api

# Set environment variables
heroku config:set SECRET_KEY=...
heroku config:set DATABASE_URL=...

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

## CLI Tool Usage

```bash
# Authentication
insighta login                           # Login with GitHub
insighta logout                          # Logout

# Profile Operations
insighta profile list                    # List profiles
insighta profile list --page 2           # Pagination
insighta profile list --gender male      # With filters
insighta profile get <id>                # View profile
insighta profile create "John Doe"       # Create profile
insighta profile delete <id>             # Delete profile
insighta profile search "adults from Nigeria"  # Search
insighta profile export                  # Export to CSV

# Help
insighta --help                          # Show help
insighta profile --help                  # Profile command help
insighta --version                       # Show version
```

## Testing

### Backend Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test app.tests

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### CLI Tests

```bash
cd cli
pytest tests/
pytest tests/ --cov
```

## Troubleshooting

### Common Issues

1. **Database connection error**
   - Check `DATABASE_URL` is correct
   - Ensure database service is running
   - Run migrations: `python manage.py migrate`

2. **OAuth not working**
   - Verify GitHub app is created
   - Check Client ID/Secret are correct
   - Confirm redirect URI matches GitHub settings

3. **Token not refreshing**
   - Check refresh token isn't blacklisted
   - Verify token hasn't expired
   - Check `SIMPLE_JWT` settings in Django

4. **CORS errors**
   - Update `CORS_TRUSTED_ORIGINS` in settings
   - Check `FRONTEND_URL` is correct
   - Verify browser is making requests to correct origin

## Monitoring & Logging

### Access Logs

Located in `logs/insighta.log`

Format:
```
API Request: GET /api/v2/profiles | User: user@example.com | IP: 192.168.1.1
API Response: GET /api/v2/profiles | Status: 200 | Duration: 0.12s
```

### Error Logs

Check logs for:
- `ERROR` level messages
- Failed authentications
- Rate limit violations
- Database errors

### Metrics to Monitor

- Request count and latency
- Error rates
- Token refresh count
- Rate limit hits
- Failed logins

## Performance Optimization

1. **Database Indexing**: Ensure frequent queries are indexed
2. **Caching**: Cache paginated results with Redis
3. **Pagination**: Always paginate large result sets
4. **Connection Pooling**: Use `conn_max_age` in database config

## Support & Documentation

- **API Docs**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **CLI Docs**: [cli/README.md](./cli/README.md)
- **Web Portal Docs**: [WEB_PORTAL_SETUP.md](./WEB_PORTAL_SETUP.md)
- **GitHub Issues**: Report bugs and feature requests

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/name`
5. Submit pull request

## Changelog

### Version 1.0.0 (2026-04-29)
- ✅ GitHub OAuth with PKCE
- ✅ JWT token management
- ✅ Role-based access control
- ✅ API versioning (v1, v2)
- ✅ CSV export
- ✅ CLI tool
- ✅ Rate limiting
- ✅ Request logging
- ✅ Natural language search
