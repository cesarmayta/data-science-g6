from flask import Flask,request,jsonify
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

app = Flask(__name__)

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
    
if __name__ == '__main__':
    app.run(debug=True)