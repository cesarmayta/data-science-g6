from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

#### CONFIGURACION DE SQLALCHEMY ####
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root2025@localhost:3306/db_g6'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### CREAMOS UNA CLASE QUE VA A CONVERTIRSE EN UNA TABLA SQL

class Car(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fuel_type = db.Column(db.String(255),nullable=False)
    gearbox = db.Column(db.String(255),nullable=False)
    milage_km = db.Column(db.Double,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    power_hp = db.Column(db.Double,nullable=False)
    engine_size = db.Column(db.Double,nullable=False)
    cylinders = db.Column(db.Double,nullable=False)
    price = db.Column(db.Double,nullable=True)
    
    def __init__(self,rooms):
        self.rooms = rooms
        
### CREAMOS UN ESQUEMA PAARA SERIALIZAR LOS DATOS
ma = Marshmallow(app)
class HousingSchema(ma.Schema):
    id = ma.Integer()
    rooms = ma.Integer()
    price = ma.Float()
    
## REGISTRAMOS LA TABLA EN LA BASE DE DATOS
db.create_all()
print('Tablas en base de datos creadas')

@app.route('/')
def index():
    context = {
        'title':'FLASK API VERSION 1.0',
        'message':'API USED CARS'
    }
    return jsonify(context)

if __name__ == '__main__':
    app.run(debug=True)

