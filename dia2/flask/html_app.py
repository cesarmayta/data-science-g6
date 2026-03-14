from flask import Flask,request,render_template

app = Flask(__name__)

@app.route('/')
def index():
    nombre_request = request.args.get('nombre','')
    return render_template('index.html',nombre=nombre_request)

@app.route('/suma',methods=['GET','POST'])
def suma():
    resultado = 0
    if request.method == 'POST':
        numero1 = request.form['num1']
        numero2 = request.form['num2']
        resultado = int(numero1) + int(numero2)
        return render_template('index.html',resultado=resultado) 

app.run(debug=True)