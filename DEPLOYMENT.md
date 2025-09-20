# Deployment Guide - dmitrybond.tech

This guide covers the complete deployment of the dmitrybond.tech project including the website, Cal.com booking system, and mailcow email server.

## Prerequisites

### Server Requirements
- **Web Server**: 2GB RAM, 2 CPU cores, 20GB SSD
- **Mail Server**: 4GB RAM, 2 CPU cores, 50GB SSD (separate server recommended)
- **OS**: Ubuntu 20.04+ or similar Linux distribution

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Domain Requirements
- Domain name: `dmitrybond.tech`
- DNS management access (nic.ru or similar)

## Step 1: Server Setup

### Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
```

### Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Step 2: Deploy Web Stack

### Clone Repository

```bash
git clone <repository-url>
cd dmitrybond.tech
```

### Configure Environment

```bash
# Copy environment files
cp env.example .env
cp cal/env.example cal/.env

# Edit configuration files
nano .env
nano cal/.env
```

### Required Environment Variables

#### Main .env file:
```env
NEXTAUTH_SECRET=your-random-secret-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

#### Cal.com .env file:
```env
DATABASE_URL=postgresql://cal:calpass@postgres:5432/cal
NEXTAUTH_URL=https://dmitrybond.tech
NEXTAUTH_SECRET=your-random-secret-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EMAIL_FROM=noreply@dmitrybond.tech
EMAIL_SERVER_HOST=mail.dmitrybond.tech
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=noreply@dmitrybond.tech
EMAIL_SERVER_PASSWORD=your-email-password
```

### Deploy Services

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## Step 3: Configure DNS

### A Records
```
@                    A         YOUR_WEB_SERVER_IP
www                  A         YOUR_WEB_SERVER_IP
mail                 A         YOUR_MAIL_SERVER_IP
```

### MX Record
```
@                    MX   10   mail.dmitrybond.tech
```

### SPF Record
```
@                    TXT       "v=spf1 a:mail.dmitrybond.tech include:amazonses.com -all"
```

### DKIM Record (configure after mailcow setup)
```
default._domainkey   TXT       "v=DKIM1; k=rsa; p=YOUR_DKIM_PUBLIC_KEY"
```

### DMARC Record
```
_dmarc               TXT       "v=DMARC1; p=none; rua=mailto:dmarc@dmitrybond.tech"
```

## Step 4: Configure Google OAuth

### Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"

### Configure OAuth Consent Screen

1. Fill in application information
2. Add authorized domains: `dmitrybond.tech`
3. Add redirect URIs:
   - `https://dmitrybond.tech/en/bookme/api/auth/callback/google`
   - `https://dmitrybond.tech/ru/bookme/api/auth/callback/google`

### Get Credentials

1. Copy Client ID and Client Secret
2. Add them to your `.env` files

## Step 5: Deploy Mailcow (Separate Server)

### On Mail Server

```bash
# Clone repository
git clone <repository-url>
cd dmitrybond.tech/mailcow

# Configure mailcow
cp mailcow.conf.example mailcow.conf
nano mailcow.conf

# Deploy mailcow
docker-compose -f docker-compose.mailcow.yml up -d
```

### Configure Mailcow

1. Access admin panel: `https://mail.dmitrybond.tech`
2. Default login: admin / admin (change immediately)
3. Create mailboxes:
   - `noreply@dmitrybond.tech`
   - `postmaster@dmitrybond.tech`
   - `abuse@dmitrybond.tech`
   - `dmarc@dmitrybond.tech`

### Get DKIM Key

1. Go to Configuration → DNS
2. Copy DKIM public key
3. Add to DNS as TXT record: `default._domainkey`

## Step 6: SSL Configuration

SSL certificates are automatically handled by Caddy with Let's Encrypt. Ensure:

1. Domain points to correct server IP
2. Ports 80 and 443 are open
3. No other web server is running on these ports

## Step 7: Configure Cal.com

### Access Cal.com Admin

1. Go to `https://dmitrybond.tech/cal`
2. Complete initial setup
3. Configure user profile
4. Set up event types

### Configure Integrations

1. Go to Settings → Integrations
2. Add Google Calendar integration
3. Test calendar sync

## Step 8: Optional SES Configuration

### For Better Email Deliverability

1. Create AWS SES account
2. Verify domain identity
3. Enable DKIM for domain
4. Create SMTP credentials
5. Configure mailcow to use SES as smarthost

### Update mailcow configuration:

```bash
# Add to mailcow.conf
SES_RELAY_HOST=email-smtp.us-east-1.amazonaws.com
SES_RELAY_PORT=587
SES_RELAY_USER=your-ses-smtp-username
SES_RELAY_PASS=your-ses-smtp-password
```

## Step 9: Testing

### Website Tests

```bash
# Check all services are running
docker-compose ps

# Test website
curl -I https://dmitrybond.tech
curl -I https://dmitrybond.tech/en/bookme

# Check SSL certificate
openssl s_client -connect dmitrybond.tech:443 -servername dmitrybond.tech
```

### Email Tests

```bash
# Test SMTP
telnet mail.dmitrybond.tech 587

# Test email delivery
echo "Test email" | mail -s "Test" test@dmitrybond.tech
```

### Booking System Tests

1. Go to `https://dmitrybond.tech/en/bookme`
2. Try to book an appointment
3. Verify email notifications are sent
4. Check Google Calendar integration

## Step 10: Monitoring and Maintenance

### Health Checks

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Check SSL certificates
docker-compose exec caddy caddy list-certificates
```

### Backup Script

Create `/opt/backup-dmitrybond.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Cal.com database
docker-compose exec postgres pg_dump -U cal cal > /backup/cal_${DATE}.sql

# Backup mailcow data
docker-compose -f mailcow/docker-compose.mailcow.yml exec mailcow tar -czf /backup/mailcow_${DATE}.tar.gz /var/lib/mailcow

# Cleanup old backups (keep 30 days)
find /backup -name "*.sql" -mtime +30 -delete
find /backup -name "*.tar.gz" -mtime +30 -delete
```

### Update Script

Create `/opt/update-dmitrybond.sh`:

```bash
#!/bin/bash
cd /opt/dmitrybond.tech

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check service health
sleep 30
docker-compose ps
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   - Check DNS propagation
   - Ensure ports 80/443 are open
   - Verify domain ownership

2. **Email Delivery Issues**
   - Check SPF/DKIM/DMARC records
   - Verify mailcow configuration
   - Check firewall settings

3. **Cal.com Not Loading**
   - Verify Google OAuth configuration
   - Check database connection
   - Review Cal.com logs

4. **Website Not Loading**
   - Check Caddy configuration
   - Verify Astro build
   - Check container logs

### Log Locations

- **Caddy**: `docker-compose logs caddy`
- **Web**: `docker-compose logs web`
- **Cal.com**: `docker-compose logs cal`
- **PostgreSQL**: `docker-compose logs postgres`
- **Mailcow**: `docker-compose -f mailcow/docker-compose.mailcow.yml logs`

## Security Considerations

1. **Change default passwords**
2. **Enable firewall**
3. **Regular security updates**
4. **Monitor logs for suspicious activity**
5. **Backup regularly**
6. **Use strong SSL/TLS configuration**

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Review configuration files
- Verify DNS settings
- Test network connectivity

Contact: support@dmitrybond.tech

