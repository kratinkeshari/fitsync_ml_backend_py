import joblib
import pandas as pd
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)
CORS(app)   # <= THIS FIXES ALL CORS ERRORS


# Initialize
model_pipeline = None
le_ex = None
le_meal = None

try:
    artifacts = joblib.load('artifacts.pkl')

    model_pipeline = artifacts.get('model')          # FIXED
    le_ex = artifacts.get('ex_encoder')              # FIXED
    le_meal = artifacts.get('meal_encoder')          

    print("Model and artifacts loaded successfully.")
except Exception as e:
    model_pipeline = None
    print(f"Error loading model: {e}")


@app.route('/predict', methods=['POST'])
def predict():
    if model_pipeline is None:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.get_json(force=True)
    gender = data.get('gender')
    goal = data.get('goal')
    bmi_category = data.get('bmi_category')

    try:
        X_in = pd.DataFrame([{
            "Gender": gender.strip(),
            "Goal": goal.strip(),
            "BMI Category": bmi_category.strip()
        }])

        y_hat = model_pipeline.predict(X_in)[0]
        # adjust indexing depending on pipeline output
        ex = le_ex.inverse_transform([y_hat[0]])[0]
        meal = le_meal.inverse_transform([y_hat[1]])[0]

        return jsonify({
            'predicted_exercise': ex,
            'predicted_meal': meal
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Lightweight health and info routes (no model call)
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'ok',
        'service': 'ml-backend',
        'endpoints': {
            'predict': 'POST /predict',
            'health': 'GET /healthz',
            'live': 'GET /livez'
        }
    }), 200


@app.route('/healthz', methods=['GET'])
def healthz():
    # Basic process health; does not touch model
    return 'ok', 200


@app.route('/livez', methods=['GET'])
def livez():
    # Liveness probe
    return 'ok', 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)

# ASGI adapter for running under Uvicorn
asgi_app = WsgiToAsgi(app)
