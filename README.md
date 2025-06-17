# TranSoft - Transportation Management System

A comprehensive transportation management system built with Django, featuring multi-tenant architecture for freight companies and end customers.

## Features

- Multi-tenant architecture
- Freight Company Portal
- End Customer Portal
- Staff Management
- User Authentication and Authorization
- Role-based Access Control

## Technology Stack

- Python 3.x
- Django 4.x
- PostgreSQL
- Bootstrap 5
- jQuery

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/transoft.git
cd transoft
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Project Structure

- `core/` - Core functionality and shared components
- `major_clients/` - Freight company management
- `end_customers/` - End customer management
- `superadmin/` - SAAS provider management
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)

## User Types

1. SAAS Provider (Superadmin)
   - Full access to all portals
   - Can manage all companies and customers

2. Freight Company Admin
   - Access to freight company portal
   - Can manage end customers and staff

3. End Customer Admin
   - Access to end customer portal
   - Can manage staff and view connected freight companies

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 