from flask import Flask, request, render_template
import os
import pickle
import numpy as np

app = Flask(__name__)

# Load the saved model
model_path = os.path.join(app.root_path, 'model.pkl')
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Could not find model.pkl at {model_path}")
with open(model_path, 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        def get_float(field_name, label):
            value = request.form.get(field_name, '').strip()
            if value == '':
                raise ValueError(f"{label} is required.")
            return float(value)

        step           = get_float('step', 'Time step')
        type_          = get_float('type', 'Transaction type')
        amount         = get_float('amount', 'Amount')
        oldbalanceOrg  = get_float('oldbalanceOrg', 'Origin balance before')
        newbalanceOrig = get_float('newbalanceOrig', 'Origin balance after')
        oldbalanceDest = get_float('oldbalanceDest', 'Destination balance before')
        newbalanceDest = get_float('newbalanceDest', 'Destination balance after')
        isFlaggedFraud = get_float('isFlaggedFraud', 'Bank flag status')

        input_data = np.array([[step, type_, amount,
                                 oldbalanceOrg, newbalanceOrig,
                                 oldbalanceDest, newbalanceDest,
                                 isFlaggedFraud]], dtype=float)

        prediction = model.predict(input_data)

        if prediction[0] == 1:
            result = "⚠️ FRAUDULENT TRANSACTION DETECTED!"
            result_class = "fraud"
        else:
            result = "✅ Transaction is Legitimate"
            result_class = "safe"

    except ValueError as ve:
        result = f"Input error: {str(ve)}"
        result_class = "fraud"
    except Exception as e:
        result = f"Prediction error: {str(e)}"
        result_class = "fraud"

    return render_template('submit.html', result=result, result_class=result_class)

if __name__ == '__main__':
    app.run(debug=True)