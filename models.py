from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    qualification = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    availability_status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    reports = db.relationship('DisasterReport', backref='reporter', lazy=True)
    volunteers = db.relationship('Volunteer', backref='user', lazy=True)
    updates = db.relationship('DisasterUpdate', backref='update_reporter', lazy=True)

class Disaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    disaster_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    affected_people = db.Column(db.Integer, default=0)
    resources_needed = db.Column(db.Text)
    coordinates = db.Column(db.String(100))  # GPS coordinates
    area_affected = db.Column(db.Float)  # in square kilometers
    estimated_damage = db.Column(db.Float)  # in dollars
    evacuation_status = db.Column(db.String(50))
    response_phase = db.Column(db.String(50))  # preparation, response, recovery
    weather_conditions = db.Column(db.Text)
    relief_camps = db.relationship('ReliefCamp', backref='disaster', lazy=True)
    updates = db.relationship('DisasterUpdate', backref='disaster', lazy=True, cascade="all, delete-orphan")
    supplies = db.relationship('Supply', backref='disaster', lazy=True)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='available')
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'))

class DisasterUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'), nullable=False)
    update_text = db.Column(db.Text, nullable=False)
    status_change = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ReliefCamp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer)
    current_occupancy = db.Column(db.Integer, default=0)
    facilities = db.Column(db.Text)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'))
    medical_facilities = db.relationship('MedicalFacility', backref='camp', lazy=True)
    supplies = db.relationship('Supply', backref='camp', lazy=True)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    skills = db.Column(db.Text)
    availability = db.Column(db.String(50))
    assigned_camp = db.Column(db.Integer, db.ForeignKey('relief_camp.id'))
    status = db.Column(db.String(50))
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

class MedicalFacility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    facility_type = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    available_beds = db.Column(db.Integer)
    staff_count = db.Column(db.Integer)
    camp_id = db.Column(db.Integer, db.ForeignKey('relief_camp.id'))
    supplies = db.relationship('MedicalSupply', backref='facility', lazy=True)

class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String(20))
    expiry_date = db.Column(db.Date)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'))
    camp_id = db.Column(db.Integer, db.ForeignKey('relief_camp.id'))

class MedicalSupply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer)
    expiry_date = db.Column(db.Date)
    facility_id = db.Column(db.Integer, db.ForeignKey('medical_facility.id'))

class EmergencyVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(50))
    registration_number = db.Column(db.String(20), unique=True)
    capacity = db.Column(db.Integer)
    status = db.Column(db.String(50))
    current_location = db.Column(db.String(200))
    assigned_disaster = db.Column(db.Integer, db.ForeignKey('disaster.id'))

class DisasterReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'))
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_type = db.Column(db.String(50))
    content = db.Column(db.Text)
    attachments = db.Column(db.String(200))  # File paths
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone_primary = db.Column(db.String(20), nullable=False)
    phone_secondary = db.Column(db.String(20))
    email = db.Column(db.String(120))
    area_of_operation = db.Column(db.String(200))
    available_24x7 = db.Column(db.Boolean, default=False)
