from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send, join_room, emit
from models import db, User, Message
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

@socketio.on('join_private_chat')
def handle_join_private(data):
    friend_id = data['friend_id']
    room_id = f"{min(current_user.id, int(friend_id))}-{max(current_user.id, int(friend_id))}"
    join_room(room_id)
    emit('room_joined', {'room_id': room_id})

@socketio.on('private_message')
def handle_private_message(data):
    msg_content = data['message']
    recipient_id = data['recipient_id']
    room_id = data['room_id']
    new_msg = Message(content=msg_content, sender_id=current_user.id, recipient_id=recipient_id)
    db.session.add(new_msg)
    db.session.commit()
    emit('message_recu', {
        'msg': msg_content, 
        'sender': current_user.username,
        'timestamp': new_msg.timestamp.strftime('%H:%M')
    }, room=room_id)

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

@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    username = request.form['username']
    friend_to_add = User.query.filter_by(username=username).first()
    
    if friend_to_add:
        if friend_to_add == current_user:
            flash("Vous ne pouvez pas vous ajouter vous-même !", 'error')
        elif friend_to_add in current_user.friends:
            flash("Vous êtes déjà amis.", 'info')
        else:
            current_user.friends.append(friend_to_add)
            friend_to_add.friends.append(current_user)
            db.session.commit()
            flash(f'{username} a été ajouté à vos amis !', 'success')
    else:
        flash("Utilisateur introuvable.", 'error')
        
    return redirect(url_for('chat'))

if __name__ == '__main__':
    socketio.run(app, debug=True)#on lance l'application avec le socket pour le coté instantané, avec debug en on pour avoir les log d'erreur