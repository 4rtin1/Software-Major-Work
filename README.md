# BitForge

A full-featured, modern web application for browsing, buying, and managing digital games. Includes user registration, authentication, inventory, admin panels, and a stylish responsive dashboard.

## Features

- **User registration and login** (with secure password hashing)
- **Game catalogue** with search, filters, and game detail pages
- **Shopping cart** for adding games and checking out
- **User inventory** to view purchased games
- **Edit account page** (email and password change)
- **Admin user management:** promote, delete users
- **Admin game management:** edit, delete games
- **Responsive dashboard** with color-coded navigation cards
- **Bootstrap 5 UI** with modern icons and layout

## Tech Stack

- **Python 3**
- **Flask** (Web framework)
- **Flask-Login** (User sessions)
- **Flask-WTF / WTForms** (Forms and validation)
- **Flask-SQLAlchemy** (ORM for SQLite database)
- **Bootstrap 5 & Bootstrap Icons** (Styling and icons)

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/gamestore-flask.git
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```
### 3. Run the app

```bash
python app.py
```
### 4. Login using test accounts

| Role   | Email                      | Password   |
|--------|----------------------------|------------|
| Admin  | admin@account.com          | 12345678   |
| User   | user@account.com           | 12345678   |
