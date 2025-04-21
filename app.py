from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passwords.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load encryption key
key_file_path = os.path.join(os.path.dirname(__file__), 'secret.key')
with open(key_file_path, "rb") as key_file:
    key = key_file.read()
fernet = Fernet(key)

# Database model
class Credential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_encrypted = db.Column(db.LargeBinary, nullable=False)

@app.route('/')
def index():
    creds = Credential.query.all()
    return render_template('index.html', creds=creds)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        password = request.form['password']
        encrypted_password = fernet.encrypt(password.encode())
        new_cred = Credential(website=website, username=username, password_encrypted=encrypted_password)
        db.session.add(new_cred)
        db.session.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/view/<int:cred_id>')
def view(cred_id):
    cred = Credential.query.get_or_404(cred_id)
    decrypted_password = fernet.decrypt(cred.password_encrypted).decode()
    return render_template('view.html', cred=cred, password=decrypted_password)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
