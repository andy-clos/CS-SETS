# CS Smart EduTrack System (CS-SETS)

Deployed Web App: https://cssets.pythonanywhere.com/

**CAT304 - Group Innovation Project and Study for Sustainability**

## 📚 Project Overview

CS Smart EduTrack System (CS-SETS) is a comprehensive web-based educational platform designed to help Computer Science students manage their academic journey effectively. The system integrates various tools and features to enhance learning, track academic progress, and foster student collaboration.

## 👥 Team Information

**Supervisor:** Dr. Vaithegy A/P Doraisamy

**Group Members:**
1. Andyclos A/L Boon Mee (22300738)
2. Kam Weng Xuan (22300683)
3. Loh Wei Ting (22300549)
4. Muhammad Ezzat Haziq bin Elhan (22300604)

## ✨ Key Features

### 📊 Academic Management
- **Dashboard** - Centralized view of academic activities and progress
- **Course Management** - Browse and manage course details
- **CGPA Calculator** - Calculate and track cumulative grade point average
- **Timetable** - Organize and view class schedules

### 🎓 Learning Tools
- **Quiz & Flashcards** - Create and practice with interactive quizzes and flashcards
- **Forum** - Discussion platform for students to share knowledge and ask questions
  - Create and view posts
  - Post approval system
- **Resume Generator** - Build professional resumes with guided templates

### 👤 User Management
- **User Authentication** - Secure login and registration with Firebase
- **Profile Management** - Personal profile customization
- **User Administration** - User management for administrators
- **Appointments** - Schedule and manage academic appointments

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 5.1.3
- **Database:** SQLite (db.sqlite3)
- **Authentication:** Firebase Admin SDK 6.6.0

### Frontend
- **CSS Framework:** Bootstrap
- **JavaScript:** Vanilla JS for interactive features

### Key Libraries & Tools
- **Firebase:** Pyrebase4 4.8.0 (Authentication & Realtime Database)
- **Machine Learning:** scikit-learn 1.6.1 (for predictive features)
- **PDF Generation:** xhtml2pdf 0.2.16
- **Data Processing:** pandas 2.2.3, numpy 2.2.2
- **Image Processing:** Pillow 11.1.0

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Firebase project credentials

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd CS-SETS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Firebase
- Ensure Firebase credentials are properly configured in `cs_sets/auth/firebase-key.json`
- Update Firebase configuration in the project settings if needed

### 4. Database Setup
```bash
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
CS-SETS/
├── app/                          # Main application directory
│   ├── static/                   # Static files (CSS, JS, images)
│   │   ├── css/                  # Stylesheets
│   │   │   └── tools/            # Tool-specific styles
│   │   ├── image/                # Image assets
│   │   └── js/                   # JavaScript files
│   ├── templates/                # HTML templates
│   │   └── Tools/                # Tool-specific templates
│   │       ├── CGPA/
│   │       ├── Forum/
│   │       ├── Quizz/
│   │       ├── Resume/
│   │       └── Timetable/
│   ├── views.py                  # View functions
│   ├── urls.py                   # URL routing
│   └── custom_filters.py         # Template filters
├── cs_sets/                      # Project configuration
│   ├── auth/                     # Authentication configs
│   │   └── firebase-key.json     # Firebase credentials
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   └── wsgi.py                   # WSGI configuration
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

## 🔧 Configuration

### Environment Variables
Ensure the following are properly configured:
- Firebase API credentials
- Database settings
- Secret key for Django

### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication and Realtime Database
3. Download the service account key and place it in `cs_sets/auth/firebase-key.json`

## 📝 Usage

### For Students
1. Register an account using the registration page
2. Log in with your credentials
3. Access various tools from the dashboard
4. Utilize CGPA calculator, timetable, and other learning tools
5. Participate in forums and discussions

### For Administrators
1. Access user management features
2. Approve forum posts
3. Manage courses and appointments
4. Monitor system usage

## 🤝 Contributing

This is an academic project for CAT304. For any questions or contributions, please contact the team members listed above.

## 📄 License

This project is developed as part of academic coursework at Universiti Sains Malaysia (USM).

## 📞 Support

For support or queries, please contact:
- Dr. Vaithegy A/P Doraisamy (Project Supervisor)
- Team members via the contact information provided above

---

**University:** Universiti Sains Malaysia (USM)  
**Course:** CAT304 - Group Innovation Project and Study for Sustainability  
**Academic Year:** 2024/2025
