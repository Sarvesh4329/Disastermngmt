from flask import Flask, render_template, request, redirect, url_for, flash, abort, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Disaster, Resource, Volunteer, ReliefCamp, EmergencyContact, DisasterUpdate, MedicalFacility, Supply
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(request.form['password'])
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_disasters = Disaster.query.order_by(Disaster.date_reported.desc()).all()
    return render_template('dashboard.html', disasters=user_disasters)

@app.route('/disaster/<int:id>')
def disaster_detail(id):
    disaster = Disaster.query.get_or_404(id)
    resources = Resource.query.filter_by(disaster_id=id).all()
    return render_template('disaster_detail.html', disaster=disaster, resources=resources)

@app.route('/resource/add/<int:disaster_id>', methods=['GET', 'POST'])
@login_required
def add_resource(disaster_id):
    disaster = Disaster.query.get_or_404(disaster_id)
    if request.method == 'POST':
        resource = Resource(
            name=request.form['name'],
            quantity=int(request.form['quantity']),
            type=request.form['type'],
            status='available',
            disaster_id=disaster_id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource added successfully!', 'success')
        return redirect(url_for('disaster_detail', id=disaster_id))
    return render_template('add_resource.html', disaster=disaster)

@app.route('/')
def index():
    disaster_type = request.args.get('type')
    severity = request.args.get('severity')
    location = request.args.get('location')
    
    query = Disaster.query
    
    if disaster_type:
        query = query.filter_by(disaster_type=disaster_type)
    if severity:
        query = query.filter_by(severity=severity)
    if location:
        query = query.filter(Disaster.location.ilike(f'%{location}%'))
    
    disasters = query.order_by(Disaster.date_reported.desc()).all()
    return render_template('index.html', disasters=disasters)

@app.route('/disaster/new', methods=['GET', 'POST'])
@login_required
def new_disaster():
    if request.method == 'POST':
        affected_people = request.form.get('affected_people')
        area_affected = request.form.get('area_affected')
        estimated_damage = request.form.get('estimated_damage')
        
        disaster = Disaster(
            title=request.form['title'],
            description=request.form['description'],
            disaster_type=request.form['type'],
            location=request.form['location'],
            severity=request.form['severity'],
            affected_people=int(affected_people) if affected_people else None,
            area_affected=float(area_affected) if area_affected else None,
            estimated_damage=float(estimated_damage) if estimated_damage else None,
            resources_needed=request.form['resources_needed'],
            status='active',
            response_phase='Initial Assessment'
        )
        db.session.add(disaster)
        db.session.commit()
        flash('Disaster report created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('new_disaster.html')

@app.route('/volunteer/register', methods=['GET', 'POST'])
@login_required
def register_volunteer():
    if request.method == 'POST':
        volunteer = Volunteer(
            user_id=current_user.id,
            skills=request.form['skills'],
            availability=request.form['availability']
        )
        db.session.add(volunteer)
        db.session.commit()
        flash('Volunteer registration successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('volunteer_register.html')

@app.route('/camp/create', methods=['GET', 'POST'])
@login_required
def create_camp():
    if request.method == 'POST':
        disaster_id = request.form.get('disaster_id')
        if not disaster_id:
            flash('Disaster ID is required', 'danger')
            return redirect(url_for('list_camps'))
            
        disaster = Disaster.query.get_or_404(disaster_id)
        camp = ReliefCamp(
            name=request.form['name'],
            location=request.form['location'],
            capacity=int(request.form['capacity']),
            facilities=request.form['facilities'],
            disaster_id=disaster_id,
            current_occupancy=0
        )
        db.session.add(camp)
        db.session.commit()
        flash('Relief camp created successfully!', 'success')
        return redirect(url_for('list_camps'))
    
    # For GET request, get list of active disasters
    active_disasters = Disaster.query.filter_by(status='active').all()
    if not active_disasters:
        flash('No active disasters found', 'warning')
        return redirect(url_for('list_camps'))
    
    return render_template('new_camp.html', disasters=active_disasters)

@app.route('/camp/<int:camp_id>')
@login_required
def camp_detail(camp_id):
    camp = ReliefCamp.query.get_or_404(camp_id)
    return render_template('camp_detail.html', camp=camp)

@app.route('/camp/<int:camp_id>/update', methods=['POST'])
@login_required
def update_camp(camp_id):
    camp = ReliefCamp.query.get_or_404(camp_id)
    camp.current_occupancy = int(request.form['current_occupancy'])
    db.session.commit()
    flash('Camp occupancy updated successfully!', 'success')
    return redirect(url_for('camp_detail', camp_id=camp_id))

@app.route('/emergency-contacts', methods=['GET', 'POST'])
@login_required
def emergency_contacts():
    if request.method == 'POST':
        contact = EmergencyContact(
            name=request.form['name'],
            organization=request.form['organization'],
            role=request.form['role'],
            phone_primary=request.form['phone_primary'],
            phone_secondary=request.form['phone_secondary'],
            email=request.form['email'],
            area_of_operation=request.form['area_of_operation'],
            available_24x7=bool(request.form.get('available_24x7'))
        )
        db.session.add(contact)
        db.session.commit()
        flash('Emergency contact added successfully!', 'success')
        return redirect(url_for('emergency_contacts'))
    contacts = EmergencyContact.query.all()
    return render_template('emergency_contacts.html', contacts=contacts)

@app.route('/disaster/<int:disaster_id>/update', methods=['POST'])
@login_required
def add_update(disaster_id):
    disaster = Disaster.query.get_or_404(disaster_id)
    if request.method == 'POST':
        update = DisasterUpdate(
            disaster_id=disaster_id,
            update_text=request.form['update_text'],
            reported_by=current_user.id
        )
        db.session.add(update)
        db.session.commit()
        flash('Update added successfully!', 'success')
        return redirect(url_for('disaster_detail', id=disaster_id))
    return redirect(url_for('disaster_detail', id=disaster_id))

@app.route('/camps')
@login_required
def list_camps():
    try:
        status = request.args.get('status')
        location = request.args.get('location')
        
        query = ReliefCamp.query.join(Disaster)
        
        if status:
            query = query.filter(Disaster.status == status)
        if location:
            query = query.filter(ReliefCamp.location.ilike(f'%{location}%'))
        
        camps = query.all()
        active_disasters = Disaster.query.filter_by(status='active').all()
        
        camp_stats = {
            'total': len(camps),
            'active': len([c for c in camps if c.disaster.status == 'active']),
            'total_capacity': sum(c.capacity or 0 for c in camps),
            'total_occupancy': sum(c.current_occupancy or 0 for c in camps)
        }

        for camp in camps:
            if camp.capacity:
                camp.occupancy_percentage = (camp.current_occupancy or 0) / camp.capacity * 100
            else:
                camp.occupancy_percentage = 0

        return render_template('camps.html', 
                            camps=camps, 
                            stats=camp_stats, 
                            active_disasters=active_disasters)
    except Exception as e:
        flash(f'Error loading camps: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/camps/export')
@login_required
def export_camps_data():
    import csv
    from io import StringIO
    import datetime
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Camp Name', 'Location', 'Capacity', 'Current Occupancy', 
                    'Facilities', 'Medical Facilities', 'Disaster', 'Status'])
    
    camps = ReliefCamp.query.all()
    for camp in camps:
        writer.writerow([
            camp.name,
            camp.location,
            camp.capacity,
            camp.current_occupancy,
            camp.facilities,
            len(camp.medical_facilities),
            camp.disaster.title,
            camp.disaster.status
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=camps_report_{datetime.date.today()}.csv'}
    )

@app.route('/camp/<int:camp_id>/medical', methods=['GET', 'POST'])
@login_required
def manage_medical_facility(camp_id):
    camp = ReliefCamp.query.get_or_404(camp_id)
    if request.method == 'POST':
        facility = MedicalFacility(
            name=request.form['name'],
            facility_type=request.form['facility_type'],
            capacity=int(request.form['capacity']),
            available_beds=int(request.form['available_beds']),
            staff_count=int(request.form['staff_count']),
            camp_id=camp_id
        )
        db.session.add(facility)
        db.session.commit()
        flash('Medical facility added successfully!', 'success')
        return redirect(url_for('camp_detail', camp_id=camp_id))
    return render_template('add_medical_facility.html', camp=camp)

@app.route('/camp/<int:camp_id>/supply', methods=['GET', 'POST'])
@login_required
def manage_camp_supply(camp_id):
    camp = ReliefCamp.query.get_or_404(camp_id)
    if request.method == 'POST':
        supply = Supply(
            item_name=request.form['item_name'],
            category=request.form['category'],
            quantity=int(request.form['quantity']),
            unit=request.form['unit'],
            expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form['expiry_date'] else None,
            camp_id=camp_id
        )
        db.session.add(supply)
        db.session.commit()
        flash('Supply added successfully!', 'success')
        return redirect(url_for('camp_detail', camp_id=camp_id))
    return render_template('add_camp_supply.html', camp=camp)

@app.route('/camp/<int:camp_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_camp(camp_id):
    camp = ReliefCamp.query.get_or_404(camp_id)
    if request.method == 'POST':
        camp.name = request.form['name']
        camp.location = request.form['location']
        camp.capacity = int(request.form['capacity'])
        camp.facilities = request.form['facilities']
        db.session.commit()
        flash('Camp details updated successfully!', 'success')
        return redirect(url_for('camp_detail', camp_id=camp_id))
    return render_template('edit_camp.html', camp=camp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
