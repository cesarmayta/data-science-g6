import joblib
import numpy as np

# Load the best model
model = joblib.load('./model/model.pkl')

# Load the scalers
scaler_X = joblib.load('./model/scaler_X.pkl')
scaler_y = joblib.load('./model/scaler_y.pkl')

print("Model and scalers loaded successfully!")

def predict_new_car_price(
    fuel_type_input: str,
    gearbox_input: str,
    mileage_km: float,
    year: float,
    power_hp: float,
    engine_size_cc: float,
    cylinders: float
) -> float:
    """
    Predicts the price of a car based on new input data.

    Args:
        fuel_type_input (str): Fuel type ('gasolina' or 'other').
        gearbox_input (str): Gearbox type ('automatic', 'manual', or 'semi-automatic').
        mileage_km (float): Mileage in kilometers.
        year (float): Manufacturing year.
        power_hp (float): Horsepower.
        engine_size_cc (float): Engine size in cubic centimeters.
        cylinders (float): Number of cylinders.

    Returns:
        float: Predicted price of the car.
    """

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


new_car_features = {
'fuel_type_input': 'gasolina',
'gearbox_input': 'manual',
'mileage_km': 50000.0,
'year': 2018.0,
'power_hp': 150.0,
'engine_size_cc': 1600.0,
'cylinders': 4.0
}

predicted = predict_new_car_price(**new_car_features)
print(f"Predicted price: {predicted:.2f} Euros")