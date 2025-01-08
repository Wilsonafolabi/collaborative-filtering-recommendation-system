import pickle
import os

# Load the KNN model
def load_knn_model():
    model_path = os.path.join('recommeder_system', 'models', 'knn_model.pkl')
    with open(model_path, 'rb') as file:
        knn_model = pickle.load(file)
    return knn_model

# Load the scaler
def load_scaler():
    scaler_path = os.path.join('recommeder_system', 'models',  'scaler.pkl')
    with open(scaler_path, 'rb') as file:
        scaler = pickle.load(file)
    return scaler
