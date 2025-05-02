import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Configure the SQLite database
db_path = os.path.join(os.getcwd(), 'data', 'patients.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Creates 'data' folder if it doesn't exist
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'isolation_level': 'SERIALIZABLE'  # Ensures the highest isolation level for concurrency
}

# Initialize the database
db = SQLAlchemy(app)

# Define the Patient model
class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    insurance_id = db.Column(db.String(50))

    appointments = db.relationship('Appointment', backref='patient', lazy=True)

# Define the Doctor model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    specialization = db.Column(db.String(100))
    email = db.Column(db.String(100))

    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

# Define the Appointment model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    time = db.Column(db.String(10))
    duration = db.Column(db.Integer, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), index=True)
    status = db.Column(db.String(20))

# Route to show main page (patient list)
@app.route('/')
def index():
    patients = Patient.query.all()
    return render_template('index.html', patients=patients)

# Route to show all appointments
@app.route('/appointments')
def appointments():
    doctor_name = request.args.get('doctor_name')
    patient_name = request.args.get('patient_name')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Appointment.query.join(Doctor).join(Patient)

    if doctor_name:
        query = query.filter(Doctor.name.ilike(f"%{doctor_name}%"))
    if patient_name:
        query = query.filter(Patient.name.ilike(f"%{patient_name}%"))
    if min_duration:
        query = query.filter(Appointment.duration >= int(min_duration))
    if max_duration:
        query = query.filter(Appointment.duration <= int(max_duration))
    if start_date:
        query = query.filter(Appointment.date >= start_date)
    if end_date:
        query = query.filter(Appointment.date <= end_date)

    appointments = query.all()
    return render_template('appointments.html', appointments=appointments)

# Route to create a new patient
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        insurance_id = request.form['insurance_id']
        
        new_patient = Patient(
            name=name,
            email=email,
            phone=phone,
            insurance_id=insurance_id
        )
        try:
            db.session.add(new_patient)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return redirect(url_for('index'))

    return render_template('add_patient.html')

# Route to create a new doctor
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        email = request.form['email']

        new_doctor = Doctor(
            name=name,
            specialization=specialization,
            email=email
        )
        try:
            db.session.add(new_doctor)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return redirect(url_for('index'))

    return render_template('add_doctor.html')

# Route to create a new appointment
@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        status = request.form['status']
        doctor_id = request.form['doctor_id']
        patient_id = request.form['patient_id']

        new_appointment = Appointment(
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            time=time,
            duration=duration,
            status=status,
            doctor_id=doctor_id,
            patient_id=patient_id
        )
        try:
            db.session.add(new_appointment)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('appointments'))

    return render_template('add_appointment.html', doctors=doctors, patients=patients)

# Route to edit an appointment
@app.route('/appointments/edit/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    if request.method == 'POST':
        appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        appointment.time = request.form['time']
        appointment.duration = request.form['duration']
        appointment.status = request.form['status']
        appointment.doctor_id = request.form['doctor_id']
        appointment.patient_id = request.form['patient_id']

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('appointments'))

    return render_template('edit_appointment.html', appointment=appointment, doctors=doctors, patients=patients)

# Route to delete an appointment
@app.route('/appointments/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    
    return redirect(url_for('appointments'))

if __name__ == '__main__':
    app.run(debug=True)
