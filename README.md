# dmitrybond.tech

Personal brand website with booking system for Dmitry Bond - Full-Stack Developer & Technical Consultant.

## Features

- 🌐 **Bilingual Website**: English and Russian content
- 📅 **Booking System**: Integrated Cal.com for appointment scheduling
- 📧 **Email System**: Mailcow for inbound email + optional SES relay
- 🍪 **GDPR/152-FZ Compliant**: Cookie consent system
- 🔒 **SSL/HTTPS**: Automatic Let's Encrypt certificates
- 🐳 **Docker**: Complete containerized deployment

## Architecture

### Web Stack
- **Frontend**: Astro with React islands
- **Styling**: Tailwind CSS with custom brand colors
- **Proxy**: Caddy with automatic SSL
- **Booking**: Cal.com embedded calendar
- **Database**: PostgreSQL for Cal.com
- **Cache**: Redis

### Email Stack
- **Mail Server**: Mailcow (Postfix, Dovecot, Rspamd)
- **SMTP Relay**: Optional AWS SES for outbound
- **Authentication**: SPF, DKIM, DMARC records

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Domain name (dmitrybond.tech)
- VPS with public IP

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dmitrybond.tech
```

### 2. Configure Environment

```bash
# Copy and configure Cal.com environment
cp cal/env.example cal/.env
# Edit cal/.env with your values
```

### 3. Deploy

```bash
# Run deployment script
./scripts/deploy.sh

# Or manually
docker-compose up -d
```

### 4. DNS Configuration

Configure these DNS records:

```
# A records
@                    A         YOUR_SERVER_IP
www                  A         YOUR_SERVER_IP
mail                 A         YOUR_MAIL_SERVER_IP

# MX record
@                    MX   10   mail.dmitrybond.tech

# SPF record
@                    TXT       "v=spf1 a:mail.dmitrybond.tech include:amazonses.com -all"

# DKIM record (get from mailcow)
default._domainkey   TXT       "v=DKIM1; k=rsa; p=YOUR_DKIM_PUBLIC_KEY"

# DMARC record
_dmarc               TXT       "v=DMARC1; p=none; rua=mailto:dmarc@dmitrybond.tech"
```

## Configuration

### Cal.com Setup

1. Create Google OAuth application:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add redirect URIs:
     - `https://dmitrybond.tech/en/bookme/api/auth/callback/google`
     - `https://dmitrybond.tech/ru/bookme/api/auth/callback/google`

2. Configure Cal.com environment variables in `cal/.env`:
   ```env
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   NEXTAUTH_SECRET=your-random-secret
   ```

### Mailcow Setup

1. Deploy mailcow on separate server:
   ```bash
   cd mailcow
   docker-compose -f docker-compose.mailcow.yml up -d
   ```

2. Access mailcow admin panel at `https://mail.dmitrybond.tech`

3. Create mailboxes and configure DKIM

### SES Relay (Optional)

For better deliverability, configure SES as smarthost:

1. Create SES domain identity
2. Configure DKIM in SES
3. Update mailcow postfix configuration
4. Add SES SMTP credentials to mailcow

## Development

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Project Structure

```
dmitrybond.tech/
├── src/
│   ├── components/          # Astro components
│   ├── layouts/            # Page layouts
│   ├── pages/              # Route pages
│   │   ├── en/             # English pages
│   │   └── ru/             # Russian pages
│   └── styles/             # Global styles
├── caddy/                  # Caddy configuration
├── cal/                    # Cal.com configuration
├── mailcow/                # Mailcow configuration
├── scripts/                # Deployment scripts
└── docker-compose.yml      # Main Docker setup
```

## Brand Colors

The website uses a custom color palette:

- **Primary**: `#E6974D` - Interface elements, active states
- **Background**: `#F8F8F8` - Main background
- **Text**: `#001111` - Primary text color
- **Accent**: `#C1D1C5` - Hover states, logo elements

## Legal Compliance

### GDPR (English)
- Cookie consent banner
- Privacy policy
- Data processing transparency
- User rights management

### 152-ФЗ (Russian)
- Политика обработки персональных данных
- Cookie consent system
- Data subject rights
- Compliance with Russian data protection laws

## Monitoring and Maintenance

### Health Checks
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# Check SSL certificates
docker-compose exec caddy caddy list-certificates
```

### Backups
```bash
# Backup Cal.com database
docker-compose exec postgres pg_dump -U cal cal > backup.sql

# Backup mailcow data
docker-compose -f mailcow/docker-compose.mailcow.yml exec mailcow tar -czf /backup/mailcow-$(date +%Y%m%d).tar.gz /var/lib/mailcow
```

## Security

- HTTPS enforced with HSTS
- Security headers configured
- CSP (Content Security Policy) enabled
- Email authentication (SPF, DKIM, DMARC)
- Regular security updates via Docker images

## Support

For technical support or questions:
- Email: support@dmitrybond.tech
- Website: https://dmitrybond.tech

## License

This project is proprietary software. All rights reserved.

