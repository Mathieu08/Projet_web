# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from database import Database
import re
import datetime

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
    articles = get_database().get_recent_articles()
    return render_template('accueil.html', articles=articles)


@app.route('/article/<identifiant>')
def article(identifiant):
    article = get_database().get_article(identifiant)
    if article is None:
        return render_template('404.html'), 404
    else:
        return render_template('article.html', article=article)


@app.route('/search')
def recherche():
    keyword = request.args.get('search')
    articles = get_database().get_articles_search(keyword)
    return render_template('recherche.html', articles=articles,
                           keyword=keyword)


@app.route('/admin')
def admin():
    articles = get_database().get_articles()
    return render_template('admin.html', articles=articles)


@app.route('/admin-nouveau')
def admin_nouveau():
    return render_template('newArticle.html')


@app.route('/admin-modif')
def admin_modif():
    article = get_database().get_article(request.args.get('identifiant'))
    titre = article[1]
    identifiant = article[2]
    paragraphe = article[5]
    return render_template('updateArticle.html', titre=titre,
                           paragraphe=paragraphe, identifiant=identifiant)


@app.route('/update', methods=['POST'])
def modifier_article():
    erreurs = []
    titre = request.form['titre']
    paragraphe = request.form['paragraphe']
    identifiant = request.form['identifiant']

    if len(titre) == 0 or len(paragraphe) == 0:
        erreurs.append("Tous les champs sont obligatoires.")

    if len(titre) > 100:
        erreurs.append("Le champ 'titre' doit contenir moins de "
                       "100 caracteres.")

    if len(paragraphe) > 500:
        erreurs.append("Le champ 'paragraphe' doit contenir moins de "
                       "500 caracteres.")

    if len(erreurs) != 0:
        return render_template('updateArticle.html', erreurs=erreurs,
                               titre=titre, paragraphe=paragraphe,
                               identifiant=identifiant)
    else:
        get_database().update_article(titre, identifiant, paragraphe)
        return redirect('/admin')


@app.route('/new', methods=['POST'])
def nouvel_article():
    erreurs = validation_formulaire(request.form)
    article_id = request.form['article_id']
    titre = request.form['titre']
    identifiant = request.form['identifiant']
    auteur = request.form['auteur']
    date_pub = request.form['date_pub']
    paragraphe = request.form['paragraphe']

    try:
        if len(date_pub) != 0:
            datetime.datetime.strptime(date_pub, '%Y-%m-%d')
    except ValueError:
        erreurs.append("Date inexistante ou format invalide. Le format du "
                       "champ 'Date de publication' doit etre: 'AAAA-MM-JJ'.")

    if get_database().get_article(identifiant) is not None:
        erreurs.append("L'identifiant existe deja.")

    if get_database().get_article_by_id(article_id) is not None:
        erreurs.append("L'id existe deja.")

    if len(erreurs) != 0:
        return render_template('newArticle.html', erreurs=erreurs,
                               article_id=article_id, titre=titre,
                               identifiant=identifiant, auteur=auteur,
                               date_pub=date_pub, paragraphe=paragraphe)
    else:
        get_database().insert_article(article_id, titre, identifiant,
                                      auteur, date_pub, paragraphe)

    return redirect('/admin')


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

    if not re.match(r'^[\.\~\w\-]*$', form['identifiant']):
        erreurs.append("Identifiant invalide. L'identifiant peut contenir des"
                       " lettres, des nombres et les caracteres ' - ' , ' _ '"
                       " , ' ~ ' , ' . ' .  Il ne doit pas contenir "
                       "d'espaces.")

    if (article_id == 0 or titre == 0 or identifiant == 0 or auteur == 0 or
            date_pub == 0 or paragraphe == 0):
        erreurs.append('Tous les champs sont obligatoires.')

    if titre > 100:
        erreurs.append("Le champ 'titre' doit contenir moins de "
                       "100 caracteres.")
    if identifiant > 50:
        erreurs.append("Le champ 'identifiant' doit contenir moins de "
                       "50 caracteres.")
    if auteur > 100:
        erreurs.append("Le champ 'auteur' doit contenir moins de "
                       "100 caracteres.")
    if paragraphe > 500:
        erreurs.append("Le champ 'paragraphe' doit contenir moins de "
                       "500 caracteres.")

    return erreurs
