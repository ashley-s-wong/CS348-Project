from app import app, db
from app import Patient, Appointment, Doctor
from datetime import datetime

# Ensure we're in the app context
with app.app_context():
    # Drop and recreate the tables
    db.drop_all()
    db.create_all()

    # Add some dummy data for Patients
    patient1 = Patient(patient_id=1, name='John Doe', email='john.doe@example.com', phone='555-1234', insurance_id='INS123')
    patient2 = Patient(patient_id=2, name='Jane Smith', email='jane.smith@example.com', phone='555-5678', insurance_id='INS456')

    # Add some dummy data for Doctors
    doctor1 = Doctor(id=1, name='Dr. Alice Green', specialization='Cardiologist', email='alice.green@example.com')
    doctor2 = Doctor(id=2, name='Dr. Bob White', specialization='Dermatologist', email='bob.white@example.com')

    # Add some dummy data for Appointments with proper date format
    appointment1 = Appointment(id=1, date=datetime.strptime('2025-03-01', '%Y-%m-%d').date(), time='10:00', duration=30, doctor_id=1, patient_id=1, status='Scheduled')
    appointment2 = Appointment(id=2, date=datetime.strptime('2025-03-02', '%Y-%m-%d').date(), time='11:00', duration=45, doctor_id=2, patient_id=2, status='Scheduled')

    # Add all records to the session
    db.session.add_all([patient1, patient2, doctor1, doctor2, appointment1, appointment2])

    # Commit the session to save changes to the database
    db.session.commit()

print("Database initialized and dummy data added successfully!")
