# ITC Single Sign-On (SSO)

A secure, centralized authentication service for IIT Bombay applications. ITC SSO enables users to authenticate once and access multiple integrated applications seamlessly.

![SSO Flow Diagram](https://files.tech-iitb.org/itcssostatic/sso-flow.png)

## Features

- **Centralized Authentication**: Single login for multiple applications
- **Secure Session Management**: 1-hour session validity with encrypted tokens
- **RESTful API**: Simple integration with any technology stack
- **Email Verification**: LDAP-based email verification for IITB students
- **Project Management**: Self-service project registration and management
- **Admin Controls**: Project verification and user management dashboard

## Tech Stack

- **Framework**: Django 5.1.2
- **Database**: PostgreSQL
- **Storage**: MinIO Object Storage
- **API**: Django REST Framework
- **Server**: Gunicorn with WhiteNoise for static files

## Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- MinIO storage instance (for media files)
- SMTP server (for email verification)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DeepakSilaych/itc_sso.git
cd itc_sso
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=itc_sso_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST_1=smtp.gmail.com
EMAIL_PORT_1=587
EMAIL_USE_TLS_1=True
EMAIL_HOST_USER_1=your-email@iitb.ac.in
EMAIL_HOST_PASSWORD_1=your-app-password

# MinIO Configuration
MINIO_STORAGE_ENDPOINT=your-minio-endpoint.com
MINIO_STORAGE_ACCESS_KEY=your-access-key
MINIO_STORAGE_SECRET_KEY=your-secret-key
MINIO_STORAGE_USE_HTTPS=True
MINIO_STORAGE_PORT=443
MINIO_STORAGE_MEDIA_BUCKET_NAME=itc-sso-media
MINIO_STORAGE_STATIC_BUCKET_NAME=itc-sso-static

# Application URL
HOST_URL=http://localhost:8000

# CORS Settings
CORS_ORIGIN_ALLOW_ALL=True
CSRF_TRUSTED_ORIGINS=https://sso.tech-iitb.org
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`

## API Integration

### Authentication Flow

1. **Redirect to SSO**

   ```
   GET https://sso.tech-iitb.org/project/{PROJECT_ID}/ssocall/
   ```

2. **Handle Callback**

   ```
   Your app receives: {YOUR_REDIRECT_URL}?accessid={SESSION_KEY}
   ```

3. **Fetch User Data**

   ```
   POST https://sso.tech-iitb.org/project/getuserdata
   Content-Type: application/json

   {
     "id": "session_key"
   }
   ```

4. **Response**
   ```json
   {
     "name": "John Doe",
     "roll": "210050001",
     "department": "Computer Science & Engineering",
     "degree": "B.Tech",
     "passing_year": 2024
   }
   ```

For detailed integration guides and code examples, visit the [Documentation](https://sso.tech-iitb.org/docs).

## Project Structure

```
itc_sso/
├── accounts/               # Main application
│   ├── models.py          # User, Profile, Project, Session models
│   ├── views.py           # Authentication and project views
│   ├── serializers.py     # API serializers
│   ├── forms.py           # User forms
│   ├── urls.py            # URL routing
│   ├── utils.py           # Helper functions
│   ├── email_utils.py     # Email handling with rotation
│   └── management/        # Management commands
│       └── commands/
│           └── sync_static.py
├── config/                # Django configuration
│   ├── settings.py        # Application settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── templates/             # HTML templates
│   ├── base.html         # Base template with Apple-inspired UI
│   ├── home.html         # Dashboard
│   ├── login.html        # Authentication
│   ├── register.html     # User registration
│   ├── documentation.html # API documentation
│   ├── projects/         # Project management templates
│   └── emails/           # Email templates
├── static/               # Static files
│   ├── img/             # Images and logos
│   └── style.css        # Additional styles
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Security Features

- **Email Verification**: Required for account activation
- **Session Encryption**: SHA-256 hashed session keys
- **CSRF Protection**: Django CSRF middleware enabled
- **Secure Cookies**: HttpOnly and Secure flags enabled
- **CORS Configuration**: Configurable allowed origins
- **Password Validation**: Django password validators
- **Rate Limiting**: 10 active logins for unverified projects

## Session Management

- **Expiration**: Sessions are valid for 1 hour
- **Uniqueness**: Each authentication creates a unique session key
- **Validation**: Automatic expiration and cleanup
- **Multi-device**: Track sessions across different devices

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

- Follow PEP 8 style guidelines
- Write descriptive commit messages
- Add docstrings to functions and classes
- Update documentation for API changes

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Configure proper `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
3. Use a production-grade database (PostgreSQL recommended)
4. Set up HTTPS with valid SSL certificates
5. Configure email server with proper credentials
6. Use environment-specific MinIO buckets

## Support

- **Documentation**: [https://sso.tech-iitb.org/docs](https://sso.tech-iitb.org/docs)
- **GitHub Issues**: [https://github.com/DeepakSilaych/itc_sso/issues](https://github.com/DeepakSilaych/itc_sso/issues)
- **Web Team**: [https://web.tech-iitb.org](https://web.tech-iitb.org)

## License

This project is maintained by the ITC Web Team, IIT Bombay.

## Acknowledgments

Developed and maintained by the [ITC Web Team](https://web.tech-iitb.org), IIT Bombay.

---

**Version**: 1.0.0  
**Last Updated**: October 2025
