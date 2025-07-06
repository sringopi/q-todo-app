# Environment Configuration Guide

## Overview

The TODO API uses environment variables for configuration management. This allows for flexible deployment across different environments (development, staging, production) without code changes.

## Configuration Files

### `.env` File
- **Purpose**: Contains actual environment variables for your local development
- **Security**: This file is **NOT** committed to version control (listed in `.gitignore`)
- **Location**: Root directory of the project (`/todo_api/.env`)

### `.env.example` File
- **Purpose**: Template showing the expected environment variables
- **Security**: Safe to commit to version control
- **Usage**: Copy to `.env` and update with actual values

## Current Configuration

### Your Current IP Address
Your `.env` file has been configured with your current IP address:

```bash
IP_ALLOWLIST=15.254.43.135
```

### Available Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `IP_ALLOWLIST` | Comma-separated list of allowed IP addresses | None | `192.168.1.100,10.0.0.50` |
| `DEBUG` | Enable debug mode | `false` | `true` |
| `APP_NAME` | Application name | `TODO API` | `My TODO App` |
| `VERSION` | Application version | `1.0.0` | `2.0.0` |
| `DATABASE_URL` | Database connection string | None | `postgresql://user:pass@localhost/db` |
| `REDIS_URL` | Redis connection string | None | `redis://localhost:6379` |
| `SECRET_KEY` | Application secret key | None | `your-secret-key-here` |

## Usage Examples

### Basic Setup
1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your values:
   ```bash
   IP_ALLOWLIST=your.ip.address.here
   DEBUG=true
   APP_NAME=My TODO API
   ```

### Multiple IP Addresses
```bash
IP_ALLOWLIST=192.168.1.100,10.0.0.50,203.0.113.1,15.254.43.135
```

### Production Configuration
```bash
DEBUG=false
APP_NAME=TODO API Production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@prod-db:5432/todoapi
REDIS_URL=redis://prod-redis:6379
```

## IP Allowlist Feature

### How It Works
- The `IP_ALLOWLIST` environment variable supports both individual IPs and CIDR ranges
- **Default Behavior**: If no `IP_ALLOWLIST` is configured or the .env file doesn't exist, **all traffic is allowed** (defaults to `0.0.0.0/0`)
- **Individual IPs**: Automatically converted to /32 (IPv4) or /128 (IPv6)
- **CIDR Ranges**: Full CIDR notation support (e.g., `192.168.1.0/24`, `10.0.0.0/8`)
- **IPv6 Support**: Full IPv6 address and range support
- **Multiple Entries**: Comma-separated list of IPs and ranges

### Current Status
- **Your IPs**: `15.254.43.135/32, 104.172.160.186/32` are currently allowlisted
- **Middleware**: Available but disabled by default (see `app/main.py`)
- **Enable**: Uncomment the middleware line in `app/main.py` to activate IP filtering

### Configuration Examples

#### Individual IPs (auto-converted to /32)
```bash
IP_ALLOWLIST=15.254.43.135,104.172.160.186
```

#### CIDR Ranges
```bash
IP_ALLOWLIST=192.168.1.0/24,10.0.0.0/8,172.16.0.0/12
```

#### Mixed IPs and CIDR Ranges
```bash
IP_ALLOWLIST=15.254.43.135,192.168.1.0/24,104.172.160.186/32
```

#### IPv6 Support
```bash
IP_ALLOWLIST=2001:db8::/32,::1,192.168.1.0/24
```

#### Allow All Traffic (default behavior)
```bash
# Option 1: Don't set IP_ALLOWLIST at all
# Option 2: Set it to empty
IP_ALLOWLIST=
# Option 3: Don't create .env file
```

### Testing IP Configuration
```bash
# Check current configuration
curl http://localhost:8000/config

# Expected response (in debug mode):
{
  "app_name": "TODO API",
  "version": "1.0.0",
  "debug": true,
  "ip_allowlist_configured": true,
  "ip_allowlist_raw": "15.254.43.135/32,104.172.160.186/32",
  "allowed_ip_ranges": ["15.254.43.135/32", "104.172.160.186/32"],
  "allowed_ranges_count": 2,
  "default_behavior": "restricted"
}
```

### Default Behavior Examples

#### No Configuration (allows all)
```json
{
  "ip_allowlist_configured": false,
  "ip_allowlist_raw": null,
  "allowed_ip_ranges": ["0.0.0.0/0", "::/0"],
  "default_behavior": "allow_all"
}
```

## Docker Integration

### Environment Variables in Docker

#### Option 1: Using .env file
```bash
# Docker will automatically load .env file
docker run -p 8000:8000 todo-api
```

#### Option 2: Explicit environment variables
```bash
docker run -p 8000:8000 \
  -e IP_ALLOWLIST=192.168.1.100 \
  -e DEBUG=true \
  todo-api
```

#### Option 3: Docker Compose with .env
```yaml
# docker-compose.yml
services:
  todo-api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
```

### Docker Environment Override
```bash
# Override specific variables
docker run -p 8000:8000 \
  --env-file .env \
  -e DEBUG=false \
  todo-api
```

## Security Best Practices

### ✅ Do's
- Keep `.env` file out of version control
- Use different `.env` files for different environments
- Use strong, unique secret keys in production
- Regularly rotate secret keys
- Use environment-specific IP allowlists

### ❌ Don'ts
- Never commit `.env` files to git
- Don't use default/weak secret keys in production
- Don't expose debug mode in production
- Don't use overly permissive IP allowlists

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading
```bash
# Check if .env file exists
ls -la .env

# Verify file contents
cat .env

# Test configuration loading
python3 -c "from app.core.config import settings; print(settings.ip_allowlist)"
```

#### 2. IP Access Denied
- Check your current IP: `curl https://ipinfo.io/ip`
- Update `.env` file with correct IP
- Restart the application

#### 3. Docker Environment Issues
```bash
# Check environment variables in container
docker run --rm todo-api env | grep IP_ALLOWLIST

# Debug container configuration
docker run --rm -it todo-api /bin/bash
```

## Development Workflow

### Local Development
1. Create/update `.env` file with your settings
2. Start the application: `./docker-test.sh run` or `make run`
3. Test configuration: `curl http://localhost:8000/config`

### Adding New Environment Variables
1. Update `app/core/config.py` with new settings
2. Add to `.env.example` with documentation
3. Update this documentation
4. Test with both local and Docker environments

## API Endpoints for Configuration

### Health Check (includes IP filtering status)
```bash
GET /health
```

### Configuration Info (debug mode only)
```bash
GET /config
```

### Root Endpoint (shows environment info)
```bash
GET /
```

## Example Responses

### Health Check Response
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "ip_filtering": "enabled"
}
```

### Configuration Response (debug mode)
```json
{
  "app_name": "TODO API",
  "version": "1.0.0",
  "debug": true,
  "ip_allowlist_configured": true,
  "allowed_ips_count": 1
}
```

This configuration system provides flexibility, security, and ease of deployment across different environments while maintaining the application's functionality and security standards.
