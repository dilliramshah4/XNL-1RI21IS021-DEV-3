from flask import Flask, request, jsonify, render_template
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load the trained model
MODEL_PATH = "scaling_model.joblib"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    X = np.array([[1, 50], [2, 30], [3, 40]])
    y = np.array([2, 1, 3])
    model = RandomForestRegressor()
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)

@app.route("/")
def home():
    return render_template("index.html")  # Frontend form for user input

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json["features"]
        prediction = model.predict([data])
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
