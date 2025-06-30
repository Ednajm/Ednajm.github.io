# RinnovoCasa - Italian Artisan Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Site-blue?style=for-the-badge)](https://ednajm.github.io)
[![Django](https://img.shields.io/badge/Django-4.2-green?style=for-the-badge&logo=django)](https://djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)](https://getbootstrap.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)](https://python.org/)

## 🏠 Overview

RinnovoCasa is a comprehensive platform that connects Italian homeowners with certified artisans for renovation and home improvement projects. Built with Django and featuring AI-powered quotes, appointment management, and a complete certification system for artisans.

## ✨ Key Features

### For Homeowners
- 🔍 **Smart Search**: Find artisans by category, location, and specialization
- 🤖 **AI-Powered Quotes**: Upload photos and get instant cost estimates
- ⭐ **Verified Reviews**: Read authentic reviews from real customers
- 📅 **Easy Booking**: Schedule appointments directly through the platform
- 💬 **Secure Messaging**: Communicate safely with artisans

### For Artisans
- 📊 **Complete Dashboard**: Manage profile, appointments, and statistics
- 🏆 **Certification System**: Upload documents and videos for verification
- 📈 **Performance Analytics**: Track profile views and client interactions
- 🤖 **AI Suggestions**: Get automated tips to improve your profile
- 💼 **Business Management**: Handle quotes, schedules, and client communications
- 📱 **Mobile Responsive**: Manage your business on any device

## 🚀 Technology Stack

- **Backend**: Django 4.2 (Python)
- **Frontend**: Bootstrap 5, jQuery, Custom CSS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django's built-in authentication
- **File Storage**: Django's media handling
- **AI Integration**: Ready for OpenAI/Gemini integration
- **Deployment**: GitHub Pages (demo) / Heroku (full app)

## 📋 Project Structure

```
rinnovo_casa/
├── artigiani/              # Artisan management app
│   ├── models.py          # Artisan profiles, appointments, documents
│   ├── views.py           # Public artisan views
│   ├── views_dashboard.py # Artisan dashboard views
│   ├── forms.py           # All artisan-related forms
│   └── urls.py            # Artisan URL patterns
├── utenti/                # User management app
│   ├── models.py          # Custom user model
│   ├── views.py           # Authentication and profiles
│   ├── register.py        # Registration forms
│   └── urls.py            # User URL patterns
├── core/                  # Core functionality
│   ├── models.py          # Shared models
│   ├── views.py           # Homepage and general views
│   └── urls.py            # Core URL patterns
├── templates/             # Django templates
│   ├── artigiani/         # Artisan templates
│   ├── utenti/            # User templates
│   └── core/              # Base templates
├── static/                # CSS, JS, images
├── media/                 # User uploaded files
└── manage.py              # Django management script
```

## 🛠 Installation & Setup

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ednajm/Ednajm.github.io.git
   cd Ednajm.github.io
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 👥 User Types & Features

### 1. **Clients (Homeowners)**
- Register and create property profiles
- Search and filter artisans
- Request quotes with AI assistance
- Book appointments
- Leave reviews

### 2. **Artisans (Craftspeople)**
- Complete registration with certification
- Comprehensive dashboard with:
  - Profile management with photo/video uploads
  - Document upload for certification
  - Appointment calendar management
  - Client message handling
  - AI-powered profile suggestions
  - Performance statistics
  - Work portfolio management

### 3. **Companies (Businesses)**
- Business profile registration
- Team management
- Project management tools

### 4. **Administrators**
- User management
- Artisan verification
- Platform statistics
- Content moderation

## 🤖 AI Features

- **Smart Quotes**: Photo analysis for cost estimation
- **Profile Optimization**: AI suggestions for artisan profiles
- **Auto-responses**: Suggested replies to client messages
- **Market Analysis**: Pricing recommendations based on area and competition

## 📱 Responsive Design

The platform is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🔐 Security Features

- Secure user authentication
- File upload validation
- CSRF protection
- XSS prevention
- Secure password handling

## 📊 Dashboard Features for Artisans

### Profile Management
- Complete business profile setup
- Photo and video portfolio
- Service categories and pricing
- Coverage area configuration

### Certification System
- Document upload (licenses, insurance)
- Video verification process
- Admin review workflow
- Certification badge display

### Business Analytics
- Profile view statistics
- Client interaction metrics
- Revenue tracking
- Performance insights

### Communication Tools
- Integrated messaging system
- Quote management
- Appointment scheduling
- Client relationship management

## 🚀 Deployment

### GitHub Pages (Demo)
The current deployment on GitHub Pages shows the static landing page demonstrating the platform's capabilities.

### Full Application Deployment
For a complete Django deployment, consider:
- **Heroku**: Easy Django deployment
- **DigitalOcean**: VPS with more control
- **AWS**: Scalable cloud deployment
- **Railway**: Modern deployment platform

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

- **Demo Site**: [https://ednajm.github.io](https://ednajm.github.io)
- **Repository**: [https://github.com/Ednajm/Ednajm.github.io](https://github.com/Ednajm/Ednajm.github.io)

---

**Built with ❤️ for the Italian artisan community**
