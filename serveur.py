from flask import Flask, render_template
from flask_socketio import SocketIO, send

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

if __name__ == '__main__':
    socketio.run(app, debug=True)#on lance l'application avec le socket pour le coté instantané, avec debug en on pour avoir les log d'erreur