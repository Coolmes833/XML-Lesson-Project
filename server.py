from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from zeep import Client
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='/')

#CORS Ayarı
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "DELETE"], "allow_headers": ["Content-Type"]}})

#MySQL Bağlantısı
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1632@127.0.0.1:3306/customer_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#Veritabanı Modeli
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    tcID = db.Column(db.String(256), unique=True, nullable=False)  # Hashlenmiş TC ID için daha uzun alan
    customerName = db.Column(db.String(100), nullable=False)
    customerSurname = db.Column(db.String(100), nullable=False)
    birthYear = db.Column(db.Integer, nullable=False)
    appointmentDate = db.Column(db.Date)
    appointmentTime = db.Column(db.Time)

with app.app_context():
    db.create_all()

#TC Kimlik Doğrulama
def verify_tc_id(tc_id, name, surname, birth_year):
    try:
        client = Client('https://tckimlik.nvi.gov.tr/Service/KPSPublic.asmx?WSDL')
        result = client.service.TCKimlikNoDogrula(
            TCKimlikNo=int(tc_id),
            Ad=name,
            Soyad=surname,
            DogumYili=int(birth_year)
        )
        return result
    except Exception as e:
        print(f"SOAP Error: {e}")
        return False

# TC Kimlik Doğrulama ve Hashleme
def hash_tc_id(tc_id):
    return generate_password_hash(tc_id)

def check_tc_id(tc_id, hashed_tc_id):
    return check_password_hash(hashed_tc_id, tc_id)

# Kullanıcı Kaydı Fonksiyonu
@app.route('/register', methods=['POST'])
def register_customer():
    data = request.json
    tc_id = data.get('tcID')
    name = data.get('customerName')
    surname = data.get('customerSurname')
    birth_year = data.get('birthYear')
    appointment_date = data.get('appointmentDate')
    appointment_time = data.get('appointmentTime')

    if not tc_id or not name or not surname or not birth_year:
        return jsonify({"error": "All fields are required"}), 400

    try:
        # TC Kimlik doğrulama
        is_valid = verify_tc_id(tc_id, name, surname, birth_year)
        if not is_valid:
            return jsonify({"error": "Invalid TC ID or Details"}), 400

# Veriyi veritabanına ekle ve hashle
        hashed_tc_id = generate_password_hash(tc_id)
        new_customer = Customer(
            customerName=name,
            customerSurname=surname,
            birthYear=birth_year,
            appointmentDate=appointment_date,
            appointmentTime=appointment_time,
            tcID=hashed_tc_id  # tcID burada kontrol edilmeli
        )
        db.session.add(new_customer)
        db.session.commit()

        return jsonify({"message": "Customer registered successfully!"}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to register customer"}), 500


# Randevuları Listele
@app.route('/appointments', methods=['GET'])
def get_appointments():
    try:
        appointments = Customer.query.all()
        appointments_list = [{
            "id": appointment.id,
            "customerName": appointment.customerName,
            "customerSurname": appointment.customerSurname,
            "birthYear": appointment.birthYear,
            "appointmentDate": appointment.appointmentDate.isoformat() if appointment.appointmentDate else None,
            "appointmentTime": appointment.appointmentTime.isoformat() if appointment.appointmentTime else None,
            "tcID": "*****"  # TC ID gizlenmiş olarak gösterilir
        } for appointment in appointments]
        return jsonify(appointments_list), 200
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return jsonify({"error": "Failed to fetch appointments"}), 500


# Randevu Silme Endpoint'i
@app.route('/delete_appointment/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        appointment = Customer.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({"message": "Appointment deleted successfully!"}), 200
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        return jsonify({"error": "Failed to delete appointment"}), 500

# Ana Sayfa
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
