from flask import Flask, render_template  #on ajoute flask et le repertoire templates qui va servir au html

app = Flask(__name__) #variable de l'app web contenant une instance de flask

@app.route("/") #quand quelqu'un cherche l'adresse racine du site, il tombre sur la fonction suivante (normal pour un index d'avoir la racine)
def home(): 
    return render_template("index.html")    #flasl accède à templates/index.html pour l'envoyé au navigateur du client

#sécurité/debugg
if __name__ == "__main__":
    app.run(debug=True) #live server pour afficher la page à chaque modif 