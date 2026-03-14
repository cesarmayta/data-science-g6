from flask import Flask

#creamos un objeto de la clase Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hola mundo con Flask primer app'

app.run(debug=True)

