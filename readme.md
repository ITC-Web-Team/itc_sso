# Django SSO Application

A Django-based Single Sign-On (SSO) application that uses roll numbers as usernames. The application features user registration, email verification, login, and password reset functionality.

## Features

- **User Registration**: Users can register using their roll number, name, branch, passing year, and course.
- **Email Verification**: After registration, users receive an email to verify their account before logging in.
- **Login**: Users can log in using their roll number and password.
- **Password Reset**: If a user forgets their password, they can request a password reset via email.
- **Profile Management**: Users can update their profile information (name, branch, passing year, course) once logged in.

## Tech Stack

- **Backend**: Django 4.x
- **Frontend**: Django Template Engine (HTML, CSS)
- **Database**: SQLite (default) or any other Django-supported database
- **Email**: SMTP-based email service for sending verification and password reset emails

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/django-sso-app.git
    cd django-sso-app
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv env
    source env/bin/activate   # For Windows: env\Scripts\activate
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root of the project to store your sensitive information:

    ```bash
    touch .env
    ```

    Add the following environment variables to the `.env` file:

    ```bash
    SECRET_KEY=your_secret_key
    EMAIL_HOST=smtp.your-email-service.com
    EMAIL_PORT=your_email_port
    EMAIL_HOST_USER=your_email_address
    EMAIL_HOST_PASSWORD=your_email_password
    EMAIL_USE_TLS=True   # or False depending on your configuration
    ```

5. Run the migrations to set up the database:

    ```bash
    python manage.py migrate
    ```

6. Create a superuser for accessing the Django admin panel:

    ```bash
    python manage.py createsuperuser
    ```

7. Run the development server:

    ```bash
    python manage.py runserver
    ```

8. Access the application at `http://127.0.0.1:8000`.

## Usage

### Registration

- Navigate to the registration page (`/register/`) and fill in the required information (roll number, name, branch, passing year, course, password).
- After submitting the form, an email will be sent to verify your account.

### Login

- Once your email is verified, you can log in with your roll number and password on the login page (`/login/`).

### Password Reset

- If you forget your password, go to the password reset page (`/reset_password/`) and enter your email address. You will receive a link to reset your password.

## Email Verification

The system ensures that users cannot log in until they have verified their email. During registration, a verification email is sent to the provided email address with a unique token. Clicking the link in the email will complete the verification process.

## Profile Management

Users can update their profile information after logging in by visiting their profile page. The following fields can be updated:
- Name
- Branch
- Passing year
- Course

## Folder Structure

```bash
django-sso-app/
│
├── sso_app/                  # Django app for SSO
│   ├── migrations/           # Django migration files
│   ├── templates/            # HTML templates
│   ├── __init__.py           # Python init file
│   ├── admin.py              # Django admin configurations
│   ├── apps.py               # App configuration
│   ├── forms.py              # Forms for registration, login, etc.
│   ├── models.py             # Models for user profiles
│   ├── urls.py               # URL routes
│   ├── views.py              # Views for handling HTTP requests
│
├── static/                   # Static assets (CSS, JS)
├── templates/                # Project-wide templates
│
├── manage.py                 # Django management script
├── .env                      # Environment variables
├── .gitignore                # Files and directories to ignore in Git
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── db.sqlite3                # SQLite database (can be changed)
└── sso_project/              # Project root directory
    ├── __init__.py
    ├── settings.py           # Django settings
    ├── urls.py               # Root URLs
    └── wsgi.py               # WSGI entry point

```

