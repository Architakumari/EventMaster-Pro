# EventMaster Pro — Event Management Web Application

EventMaster Pro is a Flask-based event management web application designed to simplify event organization, booking, and participant management. The platform provides an interactive interface for creating events, managing bookings, and monitoring event-related activities through a responsive dashboard.

---

# Features

## Event Management Features

* Event creation and management
* Participant registration and booking
* Event dashboard monitoring
* Dynamic event interfaces
* Responsive web design

## Backend Features

* Flask-based backend architecture
* CRUD operations for event handling
* SQLite database integration
* Booking management system
* Modular backend structure

## Technical Features

* Frontend and backend integration
* RESTful API support
* Responsive UI using HTML, CSS, and JavaScript
* Efficient database connectivity

---

# Tech Stack

| Category | Technologies          |
| -------- | --------------------- |
| Backend  | Flask (Python)        |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite                |
| APIs     | RESTful APIs          |
| Tools    | VS Code, Git          |

---

# Project Structure

```bash
EventMaster-Pro/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── booking.html
│   ├── create.html
│   ├── dashboard.html
│   └── home.html
│
├── app.py
├── requirements.txt
├── README.md
└── database.db
```

---

# Installation & Setup

## Clone Repository

```bash
git clone https://github.com/Architakumari/EventMaster-Pro.git
cd EventMaster-Pro
```

## Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / MacOS

```bash
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Application

```bash
python app.py
```

Application will run at:

```bash
http://127.0.0.1:5000
```

---

# Main Modules

## Event Creation

Allows users to create and manage events efficiently.

## Booking System

Supports participant registration and event booking workflows.

## Dashboard Monitoring

Provides event tracking and participant management interfaces.

## Database Management

Handles event records, booking details, and user data using SQLite.

---

# Future Improvements

* Online ticket payment integration
* Email notifications and reminders
* Admin analytics dashboard
* QR code-based event entry
* Cloud deployment support
* Multi-user authentication system

---

# Author

**Archita Kumari**

---

# License

This project is developed for educational and learning purposes.
