from flask import Flask,request,render_template

app = Flask(__name__)

@app.route('/')
def index():
    nombre_request = request.args.get('nombre','')
    return render_template('index.html',nombre=nombre_request)

app.run(debug=True)