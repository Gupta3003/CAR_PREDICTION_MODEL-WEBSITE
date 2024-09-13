from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import pickle
from flask_cors import cross_origin
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__, template_folder='template')

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
# You can replace SQLite with MySQL or PostgreSQL here
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Session configuration
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
app.permanent_session_lifetime = timedelta(days=30)  # Session duration

# Create a User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f"<User {self.username}>"

# Initialize the database schema (create tables)
with app.app_context():
    db.create_all()  # Creates all the tables with the new schema


# Load the trained model
model_path = 'car_price_prediction_model.pkl'
try:
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    print("Model loaded successfully.")
except FileNotFoundError:
    print(f"File not found: {model_path}")
except pickle.UnpicklingError as e:
    print("Error loading model: UnpicklingError:", e)
except Exception as e:
    print("An error occurred:", e)

# Home page route
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['logged_in'] = True
            session['user_id'] = user.id
            
            return render_template('prediction_form.html')
        else:
            return render_template('login.html', message="Invalid credentials. Please try again.")
    
    return render_template('login.html')

# Registration page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Simple registration validation
        if password != confirm_password:
            return render_template('register.html', message="Passwords do not match")
        
        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', message="Email already registered.")
        
        # Create a new user and save to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
       
        return render_template('register_success.html', message="Registration ID Done")
    
    return render_template('register.html')

# Reset Password page route
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Query the database for the user
        user = User.query.filter_by(email=email).first()

        if user:
            print(f"Redirecting to update password for user ID: {user.id}")

            return render_template('update_password.html', user_id=user.id)
        else:
            return render_template('reset_password.html', message="Email not found.")

    return render_template('reset_password.html')

# Update Password page route
@app.route('/update_password/<int:user_id>', methods=['GET', 'POST'])
def update_password(user_id):
    user=User.query.get(user_id)
    
    if user is None:
        logging.error(f"User with ID {user_id} not found.")
        return render_template('update_password.html', message="User not found.")
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            return render_template('update_password.html',message="Password did not match.")
        
        # Update the user's password
        user.password = new_password 
        db.session.commit()
        
        return render_template('pass_success.html',message="Password updated successfully.")

    return render_template('update_password.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'logged_in' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', username=user.username, email=user.email, password=user.password)
    return redirect(url_for('login'))


# Success page route
@app.route('/success')
def success():
    return render_template('success.html')

# Success page route
@app.route('/pass_success')
def pass_success():
    return render_template('pass_success.html')

# Success page route
@app.route('/register_success')
def register_success():
    return render_template('register_success.html')

# Prediction form page route
@app.route('/prediction', methods=['GET'])
def prediction_form():
    if 'logged_in' in session:
        return render_template('prediction_form.html')
    return render_template('Login.html')

# Prediction page route
@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    if request.method == 'POST':
        data = request.form
        try:
            expected_features = ['Kilometers_Driven', 'Mileage', 'Engine', 'Power',                'Age_of_car',
       'Seats', 'Location_Bangalore', 'Location_Chennai',
       'Location_Coimbatore', 'Location_Delhi', 'Location_Hyderabad',
       'Location_Jaipur', 'Location_Kochi', 'Location_Kolkata',
       'Location_Mumbai', 'Location_Pune', 'Fuel_Type_Diesel',
       'Fuel_Type_Electric', 'Fuel_Type_LPG', 'Fuel_Type_Petrol',
       'Transmission_Manual', 'Owner_Type_Fourth & Above', 'Owner_Type_Second',
       'Owner_Type_Third', 'Brand_Audi', 'Brand_BMW', 'Brand_Bentley',
       'Brand_Chevrolet', 'Brand_Datsun', 'Brand_Fiat', 'Brand_Force',
       'Brand_Ford', 'Brand_Honda', 'Brand_Hyundai', 'Brand_Isuzu',
       'Brand_Jaguar', 'Brand_Jeep', 'Brand_Lamborghini', 'Brand_Land Rover',
       'Brand_Mahindra', 'Brand_Maruti', 'Brand_Mercedes-Benz',
       'Brand_Mini Cooper', 'Brand_Mitsubishi', 'Brand_Nissan',
       'Brand_Porsche', 'Brand_Renault', 'Brand_Skoda', 'Brand_Smart',
       'Brand_Tata', 'Brand_Toyota', 'Brand_Volkswagen', 'Brand_Volvo',
       'Class_of_Brand_Low_class']
            
            # Create a zero-filled dataframe with the expected columns
            input_data = pd.DataFrame(0, index=[0], columns=expected_features)
            
            input_data['Kilometers_Driven'] = data['kilometersDriven']
            input_data['Mileage'] = data['mileage']
            input_data['Engine'] = data['engine']
            input_data['Power'] = data['power']
            input_data['Age_of_car'] = data['ageOfCar']
            input_data['Seats'] = data['seats']

            # Set the appropriate location column to 1
            location_column = f"Location_{data['location']}"
            if location_column in input_data.columns:
                input_data[location_column] = 1

            # Set the appropriate fuel type column to 1
            fuel_type_column = f"Fuel_Type_{data['fuelType']}"
            if fuel_type_column in input_data.columns:
                input_data[fuel_type_column] = 1
                
            # Set the appropriate transmission column to 1
            if data['transmission'] == 'Manual':
                input_data['Transmission_Manual'] = 1
                
            # Set the appropriate owner type column to 1
            owner_type_column = f"Owner_Type_{data['ownerType']}"
            if owner_type_column in input_data.columns:
                input_data[owner_type_column] = 1
            
            # Set the appropriate brand column to 1
            brand_column = f"Brand_{data['brand']}"
            if brand_column in input_data.columns:
                input_data[brand_column] = 1

            # Set the appropriate class of brand column to 1
            class_of_brand_column = f"Class_of_Brand_{data['classOfBrand']}"
            if class_of_brand_column in input_data.columns:
                input_data[class_of_brand_column] = 1

            # Check for any unexpected columns
            unexpected_columns = [col for col in input_data.columns if col not in expected_features]
            if unexpected_columns:
                logging.error(f"Unexpected columns in input data: {unexpected_columns}")
                raise ValueError(f"Unexpected columns in input data: {unexpected_columns}")

            # Making the prediction
            prediction = model.predict(input_data)
            final_price = prediction[0]

            return render_template('prediction_form.html', prediction_text=f'The predicted resale price of the car is ₹{0.1*final_price:.2f} Lakhs')
        except Exception as e:
            logging.error("An error occurred during prediction: %s", e)
            return render_template('prediction_form.html', prediction_text=f'Error: {str(e)}')

    return render_template('prediction_form.html')

if __name__ == "__main__":
    app.run(debug=True)

