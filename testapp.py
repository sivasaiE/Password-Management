from flask import Flask, render_template, request, jsonify
from Models import db, User, Website
from flask_login import current_user, login_required, LoginManager
import sqlite3


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # Load user from the database based on user_id
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
db.init_app(app)


@app.route('/')
def welcomepage():
    return render_template("welcomepage.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        phonenumber = request.form['phone']
        password = request.form['password']
        if not name or not email or not phonenumber or not password:
            return "All fields are required for signup.."
        new_user = User(username=name, email=email, phonenumber=phonenumber, password=password)
        
        # Add new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return "User signed up successfully"

    return render_template("signup.html")

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=name, email=email, password=password).first()
        if user:
            return render_template('CRUD.html', user=name)
        else:
            return "Invalid User"


    return render_template("login.html")


@app.route('/add', methods=['POST'])
@login_required
def add_website():
    if request.method=="POST":
        name = request.form['name']
        password = request.form['password']
        print(name, password)
        print(current_user)
        if current_user.is_authenticated:
            # Create a new Website object associated with the current user
            new_website = Website(user_id=current_user.id, website_name=name, website_password=password)
            
            # Add the new website to the session and commit changes
            db.session.add(new_website)
            db.session.commit()
            
            return jsonify(message="Successfully added website")
        else:
            return jsonify(message="User not logged in")
    return "invalid request.."

@app.route('/fetch', methods=['GET'])
def fetchall():
    if request.method=="GET":
        users = Website.query.all()
        
        # Convert user objects to dictionary for JSON response
        website_list = []
        for website in users:
            website_dict = {
                'id': website.id,
                'username': website.username,
                'email': website.email,
                'password': website.password
                # Add more fields as needed
            }
            website_list.append(website_dict)
        
        # Return JSON response with user details
        return jsonify(users=website_list)
    
    return "Invalid method"




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8081)