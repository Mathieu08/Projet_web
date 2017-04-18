# coding: utf8

#
# Nom: Caouette
# Prenom: Mathieu
# Code permanent: CAOM08109603
# Courriel: caouette.mathieu@courrier.uqam.ca
#

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from flask import session
from flask import Response
from flask import jsonify
from database import Database
import re
import datetime
from functools import wraps
import uuid
import hashlib
from gmail import Gmail

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


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


def is_authenticated(session):
    return "id" in session


def send_unauthorized():
    return Response('Accès interdit.\n'
                    'Vous devez être connecté pour pouvoir avoir accès.'
                    ' à cette page', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if len(username) == 0 or len(password) == 0:
        return render_template('login.html', msg="Un des champs est vide.",
                               username=username)

    if len(username) > 25:
        return render_template('login.html', msg="Nom d'utilisateur ou mot"
                               " de passe invalide.", username=username)

    user = get_database().get_user_login_info(username)
    if user is None:
        return render_template('login.html', msg="Nom d'utilisateur ou mot"
                               " de passe invalide.", username=username)

    salt = user[0]
    hashed_password = hashlib.sha512(password + salt).hexdigest()

    if hashed_password == user[1]:
        session_id = uuid.uuid4().hex
        get_database().save_session(session_id, username)
        session['id'] = session_id
        return redirect('/admin')
    else:
        return render_template('login.html', msg="Nom d'utilisateur ou mot"
                               " de passe invalide.", username=username)


@app.route('/forgot-password', methods=['GET', 'POST'])
def mdp_oublie():
    if request.method == 'GET':
        return render_template('forgot-password.html')
    else:
        email = request.form['email']
        if len(email) == 0:
            return render_template('forgot-password.html', msg="Le champ "
                                   "'email' est vide!")
        if get_database().get_user_by_email(email) is not None:
            jeton = uuid.uuid4().hex
            get_database().save_token(email, jeton)
            url = "http://localhost:5000/nouveau-mdp/%s" % jeton
            entete = "Nouveau mot de passe"
            msg = """Bonjour,\n
Veuillez appuyer sur le lien suivant afin de créer un nouveau mot de passe.\n
%s """ % url
            mail = Gmail()
            mail.envoyer_mail(email, entete, msg)
        return redirect('/confirmation')


@app.route('/nouveau-mdp/<jeton>', methods=['GET', 'POST'])
def nouveau_mdp(jeton):
    email = get_database().get_email_by_token(jeton)
    if email is None:
        return render_template('404.html'), 404
    if request.method == 'GET':
        return render_template('reset-password.html')
    else:
        password = request.form['password']
        if len(password) == 0:
            return render_template('reset-password.html', msg="Le champ est"
                                   "vide.")

        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        get_database().reset_password(email[0], salt, hashed_password)
        return redirect('/admin')


@app.route('/logout')
def logout():
    if is_authenticated(session):
        session_id = session["id"]
        session.pop('id', None)
        get_database().delete_session(session_id)

    return redirect('/admin')


@app.route('/admin')
def admin():
    if is_authenticated(session):
        articles = get_database().get_articles()
        return render_template('admin.html', articles=articles)
    else:
        return render_template('login.html')


@app.route('/admin-invitation', methods=['GET', 'POST'])
@authentication_required
def invitation():
    if request.method == 'GET':
        return render_template('invitation.html')
    else:
        email = request.form['email']
        if len(email) == 0:
            return render_template('invitation.html', msg="Le champ 'email' "
                                   "est vide!")

        if get_database().get_user_by_email(email) is not None:
            return render_template('invitation.html', msg="Cette utilisateur"
                                   " est deja membre!")

        jeton = uuid.uuid4().hex
        get_database().save_token(email, jeton)
        url = "http://localhost:5000/creation-compte/%s" % jeton
        entete = "Invitation"
        msg = """Vous avec été invité pour devenir membre de notre site.
Veuillez appuyer sur le lien suivant afin de créer votre compte.\n
%s """ % url
        mail = Gmail()
        mail.envoyer_mail(email, entete, msg)
        return redirect('/admin')


@app.route('/creation-compte/<jeton>', methods=['GET', 'POST'])
def creer_compte(jeton):
    email = get_database().get_email_by_token(jeton)
    if email is None:
        return render_template('404.html'), 404

    if request.method == 'GET':
        return render_template('createAccount.html')
    else:
        username = request.form['username']
        password = request.form['password']
        if len(username) == 0 or len(password) == 0:
            return render_template('createAccount.html', msg="Tous les "
                                   "champs sont obligatoires.")

        if len(username) > 25:
            return render_template('createAccount.html', msg="Le nom "
                                   "d'utilisateur doit avoir moins de 25"
                                   "caractères.")

        if get_database().get_user_login_info(username) is not None:
            return render_template('createAccount.html', msg="Ce nom "
                                   "d'utilisateur existe déjà.")

        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        get_database().create_user(username, email[0], salt, hashed_password)
        return redirect('/admin')


@app.route('/admin-nouveau')
@authentication_required
def admin_nouveau():
    return render_template('newArticle.html')


@app.route('/admin-modif/<identifiant>')
@authentication_required
def admin_modif(identifiant):
    article = get_database().get_article(identifiant)
    if article is None:
        return render_template('404.html'), 404
    else:
        titre = article[1]
        identifiant = article[2]
        paragraphe = article[5]
        return render_template('updateArticle.html', titre=titre,
                               paragraphe=paragraphe, identifiant=identifiant)


@app.route('/update', methods=['POST'])
@authentication_required
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
@authentication_required
def nouvel_article():
    erreurs = validation_formulaire(request.form)
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

    if len(erreurs) != 0:
        return render_template('newArticle.html', erreurs=erreurs,
                               titre=titre, identifiant=identifiant,
                               auteur=auteur, date_pub=date_pub,
                               paragraphe=paragraphe)
    else:
        get_database().insert_article(titre, identifiant, auteur,
                                      date_pub, paragraphe)

    return redirect('/admin')


@app.route('/identifiant/<titre>')
@authentication_required
def proposition_identifiant(titre):
    ident = titre.lower()
    ident = ident.replace(' ', '-')
    ident = re.sub('[^\.\~\w\-]', '', ident)

    identifiant = ident
    numero = 1
    while get_database().get_article(identifiant) is not None:
        identifiant = ident + str(1)
        numero = numero + 1

    result = {"identifiant": identifiant}
    return jsonify(result)


@app.route('/verif-identifiant/<ident>')
@authentication_required
def verification_identifiant(ident):
    if get_database().get_article(ident) is not None:
        return render_template('identifiant.html', msg="Cette identifiant "
                               "existe deja. Veuillez en entrer un nouveau.")
    else:
        return render_template('identifiant.html')


@app.route('/api/articles')
def liste_articles():
    articles = get_database().get_articles_publie()
    data = [{"titre": each[1], "auteur": each[3],
            "url": "http://localhost:5000/article/"+each[2]}
            for each in articles]
    return jsonify(data)


@app.route('/api/article/<identifiant>')
def api_article(identifiant):
    article = get_database().get_article(identifiant)
    if article is None:
        return jsonify(), 404
    else:
        data = {"titre": article[1], "identifiant": article[2],
                "auteur": article[3], "date_publication": article[4],
                "paragraphe": article[5]}
        return jsonify(data)


@app.route('/api/creer-article', methods=['POST'])
@authentication_required
def creer_article():
    data = request.get_json()
    if len(data) != 5 or not validation_json(data):
        return "Le format du json ne correspond pas au format attendu", 400

    erreurs = validation_formulaire(data)
    if get_database().get_article(data['identifiant']) is not None:
        erreurs.append("L'identifiant existe deja.")

    try:
            datetime.datetime.strptime(data['date_pub'], '%Y-%m-%d')
    except ValueError:
        erreurs.append("Date inexistante ou format invalide. Le format du "
                       "champ 'Date de publication' doit etre: 'AAAA-MM-JJ'.")

    if len(erreurs) != 0:
        return "", 400

    get_database().insert_article(data['titre'], data['identifiant'],
                                  data['auteur'], data['date_pub'],
                                  data['paragraphe'])
    return "", 201


def validation_json(data):
    valide = ['titre', 'identifiant', 'auteur', 'date_pub', 'paragraphe']
    for each in valide:
        if each not in data:
            return False
    return True


def validation_formulaire(form):
    erreurs = []
    titre_size = len(form['titre'])
    ident_size = len(form['identifiant'])
    auteur_size = len(form['auteur'])
    date_pub_size = len(form['date_pub'])
    par_size = len(form['paragraphe'])

    if not re.match(r'^[\.\~\w\-]*$', form['identifiant']):
        erreurs.append("Identifiant invalide. L'identifiant peut contenir des"
                       " lettres, des nombres et les caracteres ' - ' , ' _ '"
                       " , ' ~ ' , ' . ' .  Il ne doit pas contenir "
                       "d'espaces.")

    if (titre_size == 0 or ident_size == 0 or
            auteur_size == 0 or date_pub_size == 0 or par_size == 0):
        erreurs.append('Tous les champs sont obligatoires.')

    if titre_size > 100:
        erreurs.append("Le champ 'titre' doit contenir moins de "
                       "100 caracteres.")
    if ident_size > 50:
        erreurs.append("Le champ 'identifiant' doit contenir moins de "
                       "50 caracteres.")
    if auteur_size > 100:
        erreurs.append("Le champ 'auteur' doit contenir moins de "
                       "100 caracteres.")
    if par_size > 500:
        erreurs.append("Le champ 'paragraphe' doit contenir moins de "
                       "500 caracteres.")

    return erreurs

app.secret_key = "540346aed99a450b80d9abf439d17898"
