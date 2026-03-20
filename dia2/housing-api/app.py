from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

#### CONFIGURACION DE SQLALCHEMY ####
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root2025@localhost:3306/db_g6'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Housing(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    rooms = db.Column(db.Integer,nullable=False)
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


##### HOUSING ML ################
import joblib
import numpy as np
import sklearn

model = joblib.load('./model/model.pkl')
sc_x = joblib.load('./model/scaler_x.pkl')
sc_y = joblib.load('./model/scaler_y.pkl')

def predict_price(rooms):
    rooms_sc = sc_x.transform(np.array([[rooms]]))
    prediction = model.predict(rooms_sc)
    prediction_sc = sc_y.inverse_transform(prediction) * 1000
    price = round(float(prediction_sc[0][0]),2)
    return price



@app.route('/')
def index():
    context = {
        'title':'FLASK API VERSION 1.0',
        'message':'Bienvenido a mi API'
    }
    return jsonify(context)

@app.route('/housing_price',methods=['POST'])
def housing_price():
    rooms = request.json['rooms']
    price = predict_price(rooms)
    context = {
        'message':'precio predicho',
        'habitaciones': rooms,
        'precio': price
    }
    
    return jsonify(context)

###### RUTAS PARA HOUSING API
@app.route('/housing',methods=['POST'])
def set_data():
    rooms = request.json['rooms']
    price = predict_price(rooms)
    
    #registramos los datos en la tabla
    new_housing = Housing(rooms)
    new_housing.price = price
    db.session.add(new_housing)
    db.session.commit()
    
    data_schema = HousingSchema()
    
    context = data_schema.dump(new_housing)
    
    return jsonify(context)

    
if __name__ == '__main__':
    app.run(debug=True)