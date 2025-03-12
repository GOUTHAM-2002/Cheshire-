from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Login failed. Please check your credentials.', 'error')
    return render_template('login.html')

@app.route('/signup/<role>', methods=['GET', 'POST'])
def signup(role):
    if role not in ['customer', 'facility_owner']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            # Create auth user
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Store user profile based on role
            profile_data = {
                "user_id": response.user.id,
                "role": role,
                "email": email
            }
            
            if role == 'facility_owner':
                profile_data.update({
                    "first_name": request.form['first_name'],
                    "last_name": request.form['last_name'],
                    "phone": request.form['phone'],
                    "company_name": request.form['company_name'],
                    "company_hq": request.form['company_hq'],
                    "properties_managed": request.form['properties_managed']
                })
            else:
                profile_data.update({
                    "first_name": request.form['first_name'],
                    "last_name": request.form['last_name'],
                    "phone": request.form['phone']
                })
            
            supabase.table('profiles').insert(profile_data).execute()
            flash('Please check your email to verify your account.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash('Signup failed. Please try again.', 'error')
    
    return render_template('signup.html', role=role)

if __name__ == '__main__':
    app.run(debug=True)