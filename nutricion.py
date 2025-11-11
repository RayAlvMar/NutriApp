from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'secretishimo'

usuarios = {}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        dia = request.form['dia']
        mes = request.form['mes']
        anio = request.form['anio']
        verifica = request.form.get('verifica')

        if email in usuarios:
            return render_template('registrarse.html', error="El correo ya está registrado.")
        else:
            usuarios[email] = {'password': password,'dia': dia,'mes': mes,'anio': anio}
            session['usuario'] = email
            return redirect(url_for('diseno'))
    return render_template('registrarse.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    email = request.form['email']
    password = request.form['password']
    if email in usuarios and usuarios[email]['password'] == password:
        session['usuario'] = email
        return redirect(url_for('diseno'))
    else:
        return render_template('login.html', error="Correo o contraseña incorrectos")

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/diseno')
def diseno():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('diseno.html', usuario=session['usuario'])

@app.route('/calculadora')
def calculadora():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('calculadora.html', usuario=session['usuario'])

@app.route('/basal')
def basal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('basal.html', usuario=session['usuario'])

@app.route('/plan')
def plan():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('plan.html', usuario=session['usuario'])

@app.route('/ejercicios')
def ejercicios():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('ejercicios.html', usuario=session['usuario'])

@app.route('/consejo')
def consejo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('consejo.html', usuario=session['usuario'])

if __name__ == '__main__':
    app.run(debug=True)