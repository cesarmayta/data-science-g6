#import joblib
#import numpy as np
#import sklearn

from housing_predictor import predict_price


rooms = int(input("Ingrese el nro de habitaciones : "))
prediction = predict_price(rooms)
print(f'El precio de una casa con {rooms} habitaciones es de : $ {prediction}') 