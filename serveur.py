from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send, join_room, emit
from models import db, User, Message
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_, func

app = Flask(__name__) #création de l'application __name__
app.config['SECRET_KEY'] = 'secret' #mesure de sécurité de flask, les cookies, pour qu'un user reste connecté
socketio = SocketIO(app) #on greffe notre application au socket (permet le "instantané" de l'application)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #indique le chemin du fichier de bdd
db.init_app(app) #connexion avec models.py pour la bdd 

login_manager = LoginManager() #on cree le gestionnaire de connexion de flask
login_manager.init_app(app) #on le greffe à l'application
login_manager.login_view = 'login' #si un user va sur une page dont l'accès est bloqué sans être connecté, on redirige vers la page login

@login_manager.user_loader #prend l'utilisateur du cookie
def load_user(user_id): #prend son id
    return User.query.get(int(user_id)) #cherche l'utilisateur d'id du cookie
with app.app_context():
    db.create_all() #vérifiacation que le fichier de bdd et ses tables existent, sinon, les crées

@app.route('/') #quand on tape l'adresse du site à sa racine
@login_required #si non connecté, revoie à la page de connexion
def chat():
    return render_template('chat.html', user=current_user) #on retourne la page chat.html, dans le dossier templates avec les données de user

@app.route('/logout')
@login_required
def logout():
    logout_user() #supprime la session
    return redirect(url_for('login')) #renvoie à la page de connexion

@socketio.on('join_private_chat') #c'est aps une page mais un listener
def handle_join_private(data):
    friend_id = data['friend_id'] #extraction de l'id de la personne avec qui on parle
    room_id = f"{min(current_user.id, int(friend_id))}-{max(current_user.id, int(friend_id))}" #création d'un id pour la room de chat privé avec toujours d'id le plus haut des deux id en deuxieme et vice versa 
    join_room(room_id) #connexion de l'utilisateur à la room
    emit('room_joined', {'room_id': room_id}) #informatio nde la room joined envoyé à chat.html

@socketio.on('private_message')
def handle_private_message(data):
    msg_content = data['message'] #extraction d'infos
    recipient_id = data['recipient_id'] #extraction d'infos
    room_id = data['room_id'] #extraction d'infos
    new_msg = Message(content=msg_content, sender_id=current_user.id, recipient_id=recipient_id) #crea de l'objet message pour la bdd
    db.session.add(new_msg) #ajoute à la bdd
    db.session.commit() #commit 
    emit('message_recu', {
        'msg': msg_content, 
        'sender': current_user.username,
        'sender_id': current_user.id,
        'timestamp': new_msg.timestamp.strftime('%H:%M')
    }, room=room_id) #evoie du message à tout le monde dans la room

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': #si l'utilisateur clique sur s'inscrire
        username = request.form['username'] #extraction de l'username depuis le formulaire HTML
        password = request.form['password'] #extraction du mdp depuis le formulaire HTML

        user_exists = User.query.filter_by(username=username).first() #requete si l'utilisateur existe deja, on donne le premier venu

        if user_exists: #s'il existe un utilisateur avec le meme username
            flash('Ce pseudo est déjà pris !', 'error')
            return redirect(url_for('register')) #refresh de la page
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256') #prend le password et le hash en sha256

        new_user = User(username=username, password_hash=hashed_password) #on crée un utilisateur avec les infos
        
        db.session.add(new_user) #on envoie l'utilisateur à la bdd
        db.session.commit() #on commit l'envoie du nouvel user

        flash('Compte créé avec succès ! Connectez-vous.', 'success')
        return redirect(url_for('login')) #quuand le compte est crée, on redirige vers la page de login
    
    return render_template('register.html') #quand l'user n'a pas encore cliquer sur s'inscrire, on affiche le formulaire de connexion

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': #quand l'utilisateur clique sur se connecter
        username = request.form['username'] #extraction
        password = request.form['password'] #extraction
         
        user = User.query.filter_by(username=username).first() #recherche de l'utilisateur dans la base de données
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('chat')) #si le mot de passe est bon, on redirige vers le chat
        else:
            flash('Email ou mot de passe incorrect.', 'error')
            
    return render_template('login.html') #avant que l'utilisateur clique sur se connecter

@app.route('/add_friend', methods=['POST']) #la page n'est visible qu'en cliquant sur ajouter un amis (très bref)
@login_required
def add_friend():
    username = request.form['username'] #recup le pseudo de la requete
    friend_to_add = User.query.filter_by(username=username).first() #le cherche dans la base de données
    
    if friend_to_add: #si l'amis existe dans la base de données
        if friend_to_add == current_user: #si l'amis est soi meme, c'est non
            flash("Vous ne pouvez pas vous ajouter vous-même !", 'error')
        elif friend_to_add in current_user.friends: #si l'amis est déjà ajouté, c'est non
            flash("Vous êtes déjà amis.", 'info')
        else: #si l'amis exite, n'est pas soi meme et n'est pas deja un amis
            current_user.friends.append(friend_to_add) #ajout de la personne à la table d'amis de l'utilisateur
            friend_to_add.friends.append(current_user) #on ajoute reciproquement l'utilisateur à celle de l'amis
            db.session.commit()
            flash(f'{username} a été ajouté à vos amis !', 'success')
    else:
        flash("Utilisateur introuvable.", 'error')
        
    return redirect(url_for('chat'))

@app.route('/get_history/<int:friend_id>')
@login_required
def get_history(friend_id):
    Message.query.filter_by(sender_id=friend_id, recipient_id=current_user.id).update({'is_read': True}) #update du status des messages à lus
    db.session.commit() #update : passage des messages non lus en lus quand ont recup l'historique
    messages = Message.query.filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.recipient_id == friend_id),
            (Message.sender_id == friend_id) & (Message.recipient_id == current_user.id)
        ) #requete "trouver les message envoyer par moi et recu par mon amis ou inversement"
    ).order_by(Message.timestamp.asc()).all() #trier par timestamp
    history = [] #initialisation de la variable d'historique sous forme de liste
    for msg in messages:#pour chaque itération de messages de la requete
        history.append({
            'sender': msg.author.username,
            'msg': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M')
        }) #append de la liste d'historique en forme lisible en javascript

    return jsonify(history) #envoir des données en JSON

@app.route('/get_unread_counts')
@login_required
def get_unread_counts():
    unread_counts = db.session.query(Message.sender_id, func.count(Message.id))\
        .filter_by(recipient_id=current_user.id, is_read=False)\
        .group_by(Message.sender_id).all()
    #requete a la db du nombre de message non lus en fonction de l'username de l'expediteur 
    return jsonify(dict(unread_counts)) #on traduit la requete en json pour save

if __name__ == '__main__':
    socketio.run(app, debug=True)#on lance l'application avec le socket pour le coté instantané, avec debug en on pour avoir les log d'erreur