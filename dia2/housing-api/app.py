from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route('/')
def index():
    context = {
        'title':'FLASK API VERSION 1.0',
        'message':'Bienvenido a mi API'
    }
    return jsonify(context)

if __name__ == '__main__':
    app.run(debug=True)