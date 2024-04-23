from flask import Flask, render_template, request, jsonify, flash
from flask_login import current_user, LoginManager, login_user, logout_user
from Models import db, User, Website
from bcrypt import gensalt, hashpw, checkpw

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Website.db'
db.init_app(app)

app.config['SECRET_KEY'] = 'your_unique_secret_key'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def set_password(password):
        password_hash = hashpw(password.encode('utf-8'), gensalt(14))  # Hash password with 14 rounds
        return password_hash
def check_password(password):
    password_hash = set_password(password=password)
    return checkpw(password.encode('utf-8'), password_hash)


def authenticate(username,email, password):
    # Assuming you want to authenticate based on username:
    user = User.query.filter_by(username=username, email=email).first()
    if user and user.check_password(password):
        return user
    return None

@app.route('/')
def welcomepage():
    return render_template("welcomepage.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phonenumber = request.form['phone']
        password = request.form['password']
        print("collected form data")
        user = User.query.filter_by(username=name, email=email).first()
        print(user)
        if user:
            flash("An user with email-id already exists")
            return render_template("welcomepage.html")
        try:
            if not name or not email or not phonenumber or not password:
                return "All fields are required for signup.."
            hashed_password = set_password(password=password)
            new_user = User(username=name, email=email, phonenumber=phonenumber, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("User signed up successfully")
            return render_template('login.html')
        except Exception as e:
            return jsonify(message="error while signing up"+ str(e)), 500
    return render_template("signup.html")



@app.route('/login', methods=['POST', "GET"])
def login():
    if request.method == "POST":
        print("hai")
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            
            user = authenticate(username=name, email=email, password=password)
            if user:
                user.is_active = True
                print(user.username, user.is_active)
                db.session.commit()
                return render_template('CRUD.html', user=name)
            else:
                return "invalid Credentails..."
        except Exception as e:
            print(str(e))
            return "Invalid Request" 
    return render_template("login.html")

@app.route('/add', methods=['POST'])
def add_website():
    if request.method == "POST":
        name = request.form['name']
        website_name = request.form['websitename']
        password = request.form['password']
        current_user = User.query.filter_by(username=name).first()
        if current_user.is_active == True:
            try:
                website = Website.query.filter_by(user_id=User.id, website_name=website_name).first()
                if website:
                    return jsonify(message="website already exists please update if you want")
                new_website = Website(user_id=current_user.id, website_name=website_name, website_password=password)
                db.session.add(new_website)
                db.session.commit()
                return render_template('CRUD.HTML') # Redirect to CRUD.html after successful addition
            except Exception as e:
                return jsonify(message="Error while adding website: " + str(e)), 500
        return jsonify(message="User is currently not logged in")
    return "invalid request.."


@app.route('/fetch', methods=['GET'])
def fetchall():
    try:
        name = request.args.get('name')
        current_user = User.query.filter_by(username=name).first()
        if not current_user:
            return "Invalid User"
        current_user.is_active==True and current_user
        websites = Website.query.filter_by(user_id=current_user.id).all()
        website_list = [{'name': website.website_name, 'password': website.website_password} for website in websites]
        return jsonify(websites=website_list)
 
    except:
        return jsonify(message="No such details to display")

@app.route('/update', methods=['POST'])
def update():
    if request.method == "POST":
        name = request.form['name']
        website_name = request.form['website']
        password = request.form['password']
        current_user = User.query.filter_by(username=name).first()
        if current_user.is_active==True:
            website = Website.query.filter_by(website_name= website_name).first()
            website.website_password = password
            try:
                db.session.commit()
                return jsonify(message="Successfully updated website")
            except Exception as e:
                return jsonify(message="Error updating website: " + str(e)), 500
        return jsonify(message="User is currently not logged in")
    return "invalid request.."


@app.route('/delete', methods=["GET"])
def delete():
    if request.method=="GET":
        # Retrieve data from query parameters
        name = request.args.get('name')
        website_name = request.args.get('websitename')
        password = request.args.get('password')
        
        current_user = User.query.filter_by(username=name).first()
        if current_user and current_user.is_active:
            # Query the website details to delete
            website_details = Website.query.filter_by(user_id=current_user.id, website_name=website_name, website_password=password).first()
            if website_details:
                # Delete the website details
                db.session.delete(website_details)
                db.session.commit()
                return jsonify(message="Successfully deleted")
            else:
                return jsonify(message="Invalid Credentials")
        else:
            return jsonify(message="User is currently not logged in or does not exist")
    return "Invalid request.."

@app.route('/logout', methods=["POST"])
def logout():
    if request.method=="POST":
        name = request.form['name']
        try:
            print(name)
            current_user = User.query.filter_by(username=name).first()
            print(current_user.username, current_user.is_active)
            if current_user and current_user.is_active==True:
                current_user.is_active=False
                print(current_user.is_active)
                db.session.commit()
                print('db committed')
                flash(message="Successfully logged out")
                return render_template('welcomepage.html')  # Redirect to login page
            return "Invalid name"
        except Exception as e:
            return jsonify(message="Error while logging out: " + str(e)), 500
    return jsonify(message="Invalid Request")

@app.errorhandler(404)
def not_found(error):
    return jsonify(message="Not found"), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify(message="Internal server error"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8081)
