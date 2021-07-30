from flask import Flask,render_template
import os
import json

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/crypto/<crypto>")
def choose(crypto):
    try:
        fp = open(f'./data/{crypto}/m2020.json','r')

        return render_template("choice.html",crypto=)
    except:
        return render_template("choice.html",crypto=crypto) 


if __name__=="__main__":
    app.run(debug=True)
