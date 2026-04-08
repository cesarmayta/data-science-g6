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
    
    # def __init__(self, fuel_type, gearbox, milage_km, year, power_hp, engine_size, cylinders, price=None):
    #     self.fuel_type = fuel_type
    #     self.gearbox = gearbox
    #     self.milage_km = milage_km
    #     self.year = year
    #     self.power_hp = power_hp
    #     self.engine_size = engine_size
    #     self.cylinders = cylinders
    #     self.price = price
    
        
### CREAMOS UN ESQUEMA PAARA SERIALIZAR LOS DATOS
ma = Marshmallow(app)
class CarSchema(ma.Schema):
    id = ma.Integer()
    fuel_type = ma.Str()
    gearbox = ma.Str()
    milage_km = ma.Float()
    year = ma.Int()
    power_hp = ma.Float()
    engine_size = ma.Float()
    cylinders = ma.Float()
    price = ma.Float()
    
## REGISTRAMOS LA TABLA EN LA BASE DE DATOS
db.create_all()
print('Tablas en base de datos creadas')

##### HOUSING ML ################
import joblib
import numpy as np
import sklearn

# Load the best model
model = joblib.load('./model/model.pkl')

# Load the scalers
scaler_X = joblib.load('./model/scaler_X.pkl')
scaler_y = joblib.load('./model/scaler_y.pkl')

def predict_new_car_price(
    fuel_type_input: str,
    gearbox_input: str,
    mileage_km: float,
    year: float,
    power_hp: float,
    engine_size_cc: float,
    cylinders: float
) -> float:

    # Encode Fuel_Type (0.0 for 'gasolina', 1.0 for 'other')
    encoded_fuel_type = 0.0 if fuel_type_input.lower() == 'gasolina' else 1.0

    # Encode Gearbox (one-hot encoding)
    gearbox_automatic = 0.0
    gearbox_manual = 0.0
    gearbox_semi_automatic = 0.0

    if gearbox_input.lower() == 'automatico':
        gearbox_automatic = 1.0
    elif gearbox_input.lower() == 'manual':
        gearbox_manual = 1.0
    elif gearbox_input.lower() == 'semi-automatico':
        gearbox_semi_automatic = 1.0
    else:
        raise ValueError("Invalid gearbox_input. Must be 'automatic', 'manual', or 'semi-automatic'.")

    # Create the input array in the correct order
    # The order of columns was: ['Fuel_Type', 'Gearbox_Automatic', 'Gearbox_Manual',
    # 'Gearbox_Semi-automatic', 'Mileage_km', 'Year', 'Power_hp', 'Engine_Size_cc', 'Cylinders']
    new_data = np.array([[encoded_fuel_type,
                          gearbox_automatic,
                          gearbox_manual,
                          gearbox_semi_automatic,
                          mileage_km,
                          year,
                          power_hp,
                          engine_size_cc,
                          cylinders]])

    # Scale the new data using the loaded scaler_X
    new_data_scaled = scaler_X.transform(new_data)

    # Make a prediction using the loaded model
    prediction_scaled = model.predict(new_data_scaled)

    # Inverse transform the prediction to get the original price scale
    predicted_price = scaler_y.inverse_transform(prediction_scaled.reshape(-1, 1))[0][0]

    return predicted_price

@app.route('/')
def index():
    context = {
        'title':'FLASK API VERSION 1.0',
        'message':'API USED CARS'
    }
    return jsonify(context)


###### RUTAS PARA CAR API
@app.route('/car',methods=['POST'])
def set_data():
    data = request.json
    fuel_type = data.get('fuel_type')
    gearbox = data.get('gearbox')
    mileage_km = data.get('mileage_km')
    year = data.get('year')
    power_hp = data.get('power_hp')
    engine_size = data.get('engine_size')
    cylinders = data.get('cylinders')
    
    new_car_features = {
        'fuel_type_input': fuel_type,
        'gearbox_input': gearbox,
        'mileage_km': mileage_km,
        'year': year,
        'power_hp': power_hp,
        'engine_size_cc': engine_size,
        'cylinders': cylinders
    }

    price = predict_new_car_price(**new_car_features)
    
    
    #registramos los datos en la tabla
    new_car = Car()
    new_car.fuel_type=fuel_type
    new_car.gearbox = gearbox
    new_car.milage_km = mileage_km
    new_car.year = year
    new_car.power_hp = power_hp
    new_car.engine_size = engine_size
    new_car.cylinders = cylinders
    new_car.price = price
    
    db.session.add(new_car)
    db.session.commit()
    
    data_schema = CarSchema()
    
    context = data_schema.dump(new_car)
    
    return jsonify(context)

@app.route('/car',methods=['GET'])
def get_data():
    data = Car.query.all() # select * from housing
    data_schema = CarSchema(many=True)
    return jsonify(data_schema.dump(data))

if __name__ == '__main__':
    app.run(debug=True)

