from flask import Flask,request

#creamos un objeto de la clase Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hola mundo con Flask primer app'

@app.route('/saludo')
def saludo():
    nombre = request.args.get('nombre','')
    return f"<h1>Hola {nombre}</h1>"

@app.route('/sumar/<int:a>/<int:b>')
def sumar(a,b):
    resultado =  a + b
    return f"<center>La suma de {a} + {b} es {resultado} </center>"

app.run(debug=True)

