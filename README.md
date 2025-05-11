# Disaster Management System

A comprehensive web application for managing disaster response and relief operations.

## Features

- **Disaster Tracking**: Monitor and manage active disasters with real-time updates
- **Relief Camp Management**: Track camps, occupancy, and available facilities
- **Resource Management**: Monitor and allocate resources for disaster relief
- **Volunteer Management**: Register and coordinate volunteer efforts
- **Medical Facility Tracking**: Monitor medical facilities and their capacities
- **Supply Chain Management**: Track and manage relief supplies
- **Emergency Contact Directory**: Maintain emergency contact information

## Technology Stack

- **Backend**: Python/Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Bootstrap 5, HTML/CSS, JavaScript
- **Authentication**: Flask-Login
- **Icons**: Font Awesome

## Installation

1. Clone the repository
2. Set up a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
python app.py
```

## Project Structure

```
Disastermngmt/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Project dependencies
├── static/
│   └── css/
│       └── style.css   # Custom styles
└── templates/          # HTML templates
    ├── base.html
    ├── dashboard.html
    ├── camps.html
    └── ...
```

## Key Features Documentation

### Disaster Management
- Create and track disaster incidents
- Update disaster status and response phases
- Monitor affected areas and populations

### Relief Camps
- Create and manage relief camps
- Track camp occupancy and capacity
- Manage medical facilities within camps
- Monitor supplies and resources

### Resource Management
- Track available resources
- Manage supply distribution
- Monitor medical supplies and equipment

### User Management
- User authentication and authorization
- Volunteer registration and management
- Role-based access control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
