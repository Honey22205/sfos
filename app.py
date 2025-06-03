from flask import Flask, render_template, request, make_response,flash
import io,random
import joblib
import pandas as pd
import numpy as np
app = Flask(__name__)
app.secret_key = 'secret123'

model = joblib.load('billing_model.pkl')
part_encoder = joblib.load('part_encoder.pkl')
country_encoder = joblib.load('country_encoder.pkl')
target_encoder = joblib.load('target_encoder.pkl')

countries = [
    "India", "USA", "UK", "Germany", "France", 
    "Canada", "Australia", "Brazil", "China", "Japan"
]

spare_parts = [
    {'name': 'Resistor', 'market_price': 10},
    {'name': 'Capacitor', 'market_price': 50},
    {'name': 'Inductor', 'market_price': 120},
    {'name': 'Diode', 'market_price': 8},
    {'name': 'Transistor', 'market_price': 70},
    {'name': 'Integrated Circuit', 'market_price': 500},
    {'name': 'Relay', 'market_price': 300},
    {'name': 'Transformer', 'market_price': 1500},
    {'name': 'Fuse', 'market_price': 20},
    {'name': 'Switch', 'market_price': 80},
    {'name': 'LED', 'market_price': 5},
    {'name': 'Potentiometer', 'market_price': 250},
    {'name': 'Microcontroller', 'market_price': 1200},
    {'name': 'Crystal Oscillator', 'market_price': 60},
    {'name': 'Heat Sink', 'market_price': 450},
    {'name': 'Battery', 'market_price': 2500},
    {'name': 'Connector', 'market_price': 90},
    {'name': 'Capacitor Electrolytic', 'market_price': 40},
    {'name': 'PCB Board', 'market_price': 700},
    {'name': 'Sensor', 'market_price': 1800},
    {'name': 'Antenna', 'market_price': 550}
]


@app.route('/')
def home():
    return render_template('index.html')

# Route for the parts comparison page
@app.route('/compare', methods=['GET', 'POST'])
def compare():
    part_names = [part['name'] for part in spare_parts]  # For dropdown
    
    if request.method == 'POST':
        part_name = request.form.get('part_name')
        tender_price = float(request.form.get('tender_price'))
    
        # Generate a random market price (demo)
        market_price = round(random.uniform(0.5, 2.5), 2)  
        difference = market_price - tender_price
        if tender_price <= market_price:
           recommendation = "Accept Tender"
        else:
            recommendation = "Re-evaluate Pricing"


        result = {
            'market_price': market_price,
            'tender_price': tender_price,
            'difference': round(difference, 2),
            'recommendation': recommendation
        }
        savings_percent = round(((market_price - tender_price) / market_price) * 100, 2)
        result['savings_percent'] = savings_percent

        return render_template('compare.html', result=result, parts=part_names)
    
    return render_template('compare.html', parts=part_names)
# Route for the billing page
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    part_names = [part['name'] for part in spare_parts]
    countries = [
        'India', 'United States', 'United Kingdom', 'Canada', 'Australia',
        'Germany', 'France', 'Japan', 'China', 'Brazil'
    ]

    if request.method == 'POST':
        part_name = request.form.get('part')
        quantity = int(request.form.get('quantity'))
        country = request.form.get('country')
        tender_price = float(request.form.get('tender_price'))
        
        # Find the part in spare_parts data
        part = next((item for item in spare_parts if item['name'].lower() == part_name.lower()), None)
        
        if part:
            rate = part['market_price']
            total_cost = rate * quantity
            tax = round(total_cost * 0.18, 2)
            final_amount = total_cost + tax
            
            # Compare tender price and give recommendation
            if tender_price <= rate:
                recommendation = "Accept Tender"
            else:
                recommendation = "Re-evaluate Pricing"

            bill = {
                'unit_price': rate,
                'quantity': quantity,
                'tax': tax,
                'total': final_amount,
                'recommendation': recommendation,
                'country': country
            }

            return render_template('billing.html', bill=bill, parts=part_names, countries=countries)

        else:
            error = "Part not found."
            return render_template('billing.html', error=error, parts=part_names, countries=countries)

    return render_template('billing.html', parts=part_names, countries=countries)

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    # Placeholder stats
    stats = {
        'total_parts': len(spare_parts),
        'avg_profit_gap': 'N/A (Tender prices not stored)',
        'top_selling': 'Resistor'  # Example placeholder value
    }
    return render_template('dashboard.html', stats=stats)

# Route for the settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    recommendation = None
    if request.method == 'POST':
        try:
            # Get form data
            part_name = request.form['part_name']
            country = request.form['country']
            quantity = int(request.form['quantity'])
            tender_price = float(request.form['tender_price'])

            # Encode categorical inputs
            part_encoded = part_encoder.transform([part_name])[0]
            country_encoded = country_encoder.transform([country])[0]

            # Prepare model input (features order must match training)
            features = pd.DataFrame([[part_encoded, country_encoded, quantity, tender_price]],
                        columns=['part_name', 'country', 'quantity', 'tender_price'])

            # Predict recommendation (model predicts encoded labels)
            pred_encoded = model.predict(features)[0]

            # Decode prediction to original label
            recommendation = target_encoder.inverse_transform([pred_encoded])[0]

            flash(f"Recommendation: {recommendation}", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "error")

    return render_template('settings.html',
                           part_name='',
                           country='',
                           quantity='',
                           tender_price='',
                               recommendation=recommendation)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
