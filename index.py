# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect

app = Flask(__name__)

@app.route('/')
def accueil():
	return render_template('accueil.html')