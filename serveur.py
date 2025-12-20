from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send
from models import db, User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__) #création de l'application __name__
app.config['SECRET_KEY'] = 'secret!' #mesure de sécurité de flask
socketio = SocketIO(app) #on greffe notre application au socket (permet le instantané)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #localisation du fichier de bdd
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
with app.app_context():
    db.create_all()

@app.route('/') #quand on tape l'adresse du site à sa racine
@login_required
def chat():
    return render_template('chat.html', user=current_user) #on retourne la page chat.html, dans le dossier templates

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('message') #on met le serveur en écoute du moindre evenement
def handle_message(msg): #msg=le message envoyé
    print('Message reçu du client: ' + msg) #le print est dans le terminale, c'est orienté dev
    send(msg, broadcast=True) #envoie le message en broadcast

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': #si l'utilisateur envoie des données
        username = request.form['username'] #extraction des infos envoyées dans le form de la page
        password = request.form['password']

        user_exists = User.query.filter_by(username=username).first() #requete si l'utilisateur existe deja, on donne le premier venu
        if user_exists: #s'il existe un utilisateur avec le meme username
            flash('Ce pseudo est déjà pris !', 'error')
            return redirect(url_for('register')) #refresh de la page
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256') #prend le password et le hash en sha256

        new_user = User(username=username, password_hash=hashed_password) #on crée un utilisateur avec les infos
        
        db.session.add(new_user) #on envoie l'utilisateur
        db.session.commit() #on l'ajoute

        flash('Compte créé avec succès ! Connectez-vous.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
            
    return render_template('login.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)#on lance l'application avec le socket pour le coté instantané, avec debug en on pour avoir les log d'erreur