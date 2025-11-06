from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']

    if usuario == "admin" and contrasena == "1234":
        return redirect(url_for('diseno'))
    else:
        return render_template('login.html', error="Usuario o contraseña incorrectos")

@app.route('/diseno')
def diseno():
    return render_template('diseno.html')

@app.route('/calculadora')
def calculadora():
    return render_template('calculadora.html')

@app.route('/basal')
def basal():
    return render_template('basal.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/ejercicios')
def ejercicios():
    return render_template('ejercicios.html')

@app.route('/consejo')
def consejo():
    return render_template('consejo.html')

if __name__ == '__main__':
    app.run(debug=True)
