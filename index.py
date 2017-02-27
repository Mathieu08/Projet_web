# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from database import Database

app = Flask(__name__, static_url_path="", static_folder="static")

def get_database():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()
    

@app.route('/')
def accueil():
    articles = get_database().get_articles()
    return render_template('accueil.html', articles=articles)

@app.route('/article/<identifiant>')
def article(identifiant):
    article = get_database().get_article(identifiant)
    if article is None:
        return render_template('404.html'), 404
    else:
        return render_template('article.html', article=article)

@app.route('/search', methods=['POST'])
def recherche():
    articles = get_database().get_articles_search(request.form['search'])
    return render_template('recherche.html', articles=articles)

@app.route('/admin')
def admin():
    articles = get_database().get_articles()
    return render_template('admin.html', articles=articles)

@app.route('/admin-nouveau')
def admin_nouveau():
    return render_template('newArticle.html')

@app.route('/new', methods=['POST'])
def nouvel_article():
    erreurs = validation_formulaire(request.form)

    if get_database().get_article(request.form['identifiant']) is not None:
        erreurs.append("L'identifiant existe deja.")

    if get_database().get_article_by_id(request.form['article_id']) is not None:
        erreurs.append("L'id existe deja.")

    if len(erreurs) != 0:
        return render_template('newArticle.html', erreurs=erreurs)

    return redirect('/')

def validation_formulaire(form):
    erreurs = []
    article_id = len(form['article_id'])
    titre = len(form['titre'])
    identifiant = len(form['identifiant'])
    auteur = len(form['auteur'])
    date_pub = len(form['date_pub'])
    paragraphe = len(form['paragraphe'])

    if not form['article_id'].isdigit() and article_id != 0:
        erreurs.append("Le champ 'Id' doit etre un nombre.")

    if (article_id == 0 or titre == 0 or identifiant == 0 or auteur == 0 or
        date_pub == 0 or paragraphe == 0):
        erreurs.append('Tous les champs sont obligatoires.')
    
    if titre > 100:
        erreurs.append("Le champ 'titre' doit contenir moins de 100 caracteres.")
    if identifiant > 50:
        erreurs.append("Le champ 'identifiant' doit contenir moins de 50 caracteres.")
    if auteur > 100:
        erreurs.append("Le champ 'auteur' doit contenir moins de 100 caracteres.")
    if paragraphe > 500:
        erreurs.append("Le champ 'paragraphe' doit contenir moins de 500 caracteres.")
        
    return erreurs
        
        
