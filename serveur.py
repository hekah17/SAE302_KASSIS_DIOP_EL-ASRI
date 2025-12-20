from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask_socketio import SocketIO, send
from models import db, User

app = Flask(__name__) #création de l'application __name__
app.config['SECRET_KEY'] = 'secret!' #mesure de sécurité de flask
socketio = SocketIO(app) #on greffe notre application au socket (permet le instantané)

@app.route('/') #quand on tape l'adresse du site à sa racine
def index():
    return render_template('chat.html') #on retourne la page chat.html, dans le dossier templates

@socketio.on('message') #on met le serveur en écoute du moindre evenement
def handle_message(msg): #msg=le message envoyé
    print('Message reçu du client: ' + msg) #le print est dans le terminale, c'est orienté dev
    send(msg, broadcast=True) #envoie le message en broadcast

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Ce pseudo est déjà pris !', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('Compte créé avec succès ! Connectez-vous.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)#on lance l'application avec le socket pour le coté instantané, avec debug en on pour avoir les log d'erreur