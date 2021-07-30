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
    months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    try:
        fp = open(f'./data/{crypto}/m2020.json','r')
        data = json.load(fp)
        data['months']=months
        data['currency']=crypto.capitalize()
        return render_template("choice.html",data=data)
    except:
        return render_template("choice.html",data={"message":"not found"}) 


if __name__=="__main__":
    app.run(debug=True)
