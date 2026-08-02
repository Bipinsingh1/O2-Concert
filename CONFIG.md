# Configuration & Local Setup Guide

This guide covers how to install and run the project with its configured MySQL database. XAMPP/phpMyAdmin is supported for local development.

---

## Local Installation

### Requirements

- Python 3.11 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone <repo-url>
cd ticket_system

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Create a superuser / staff account
python manage.py createsuperuser

# 5. (Optional) Seed demo ticket categories
python manage.py seed_data

# 6. Start the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000`.

---

## Database Configuration

The project now uses **MySQL by default**. The connection is configured in `config/settings.py` and can be changed with `DB_*` environment variables.

---

## MySQL via XAMPP / phpMyAdmin (Current)

### 1. Start XAMPP

- Open the XAMPP Control Panel
- Start **Apache** and **MySQL**
- Open **phpMyAdmin** at `http://localhost/phpmyadmin`

### 2. Create a database

- Click **New** in the left sidebar
- Name it `o2concert_db` (or set `DB_NAME` to another name)
- Set collation to `utf8mb4_unicode_ci`
- Click **Create**

### 3. Install the MySQL driver

```bash
pip install -r requirements.txt
```

The project uses PyMySQL, which is already listed in `requirements.txt` and registered in `config/__init__.py`.

### 4. Update `config/settings.py`

The current `DATABASES` setting is:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='o2concert_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

---

## Optional Alternative — PostgreSQL

### 1. Install PostgreSQL

Download and install from [https://www.postgresql.org/download](https://www.postgresql.org/download).

During installation note the:
- Port (default `5432`)
- Superuser username (default `postgres`)
- Password you set

### 2. Create a database

Open **pgAdmin** or the `psql` shell:

```sql
CREATE DATABASE o2_ticket_system;
CREATE USER ticket_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE o2_ticket_system TO ticket_user;
```

Or using the `psql` command line:

```bash
psql -U postgres
```

Then run the SQL commands above.

### 3. Install the PostgreSQL driver

```bash
pip install psycopg2-binary
```

### 4. Update `config/settings.py`

Replace the `DATABASES` block with:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'o2_ticket_system',   # database name you created
        'USER': 'ticket_user',         # the user you created
        'PASSWORD': 'yourpassword',    # the password you set
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

---

## Environment Variables (Optional)

You can store sensitive settings in a `.env` file instead of editing `settings.py` directly.
Create a `.env` file inside the `ticket_system/` directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=o2concert_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

The project uses `python-decouple` to read this file automatically.

---

## Quick Reference

| Task                        | Command                              |
|-----------------------------|--------------------------------------|
| Install dependencies        | `pip install -r requirements.txt`    |
| Run migrations              | `python manage.py migrate`           |
| Create superuser            | `python manage.py createsuperuser`   |
| Seed demo data              | `python manage.py seed_data`         |
| Start development server    | `python manage.py runserver`         |
| Run tests                   | `python manage.py test`              |
