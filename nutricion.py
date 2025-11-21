from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'secretishimo'

usuarios = {}

API_KEY = "0zYsgNsAc070fgtRWyul1pOkENLlfu32g3alFq3a"
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def buscar_alimento():
    alimentos = request.form.get('alimentos', '').strip()
    if not alimentos:
        flash('Por favor ingresa uno o varios alimentos.', 'error')
        return redirect(url_for('index'))

    lista_alimentos = [a.strip() for a in alimentos.split(',') if a.strip()]
    if len(lista_alimentos) > 5:
        flash('Solo puedes buscar hasta 5 alimentos.', 'error')
        return redirect(url_for('index'))

    resultados = []

    for alimento in lista_alimentos:
        try:
            params = {"query": alimento, "pageSize": 1, "api_key": API_KEY}
            resp = requests.get(API_URL, params=params)

            if resp.status_code == 200:
                data = resp.json()
                if "foods" in data and len(data["foods"]) > 0:
                    food = data["foods"][0]
                    nutrients = {n["nutrientName"]: n["value"] for n in food["foodNutrients"] if "value" in n}

                    resultados.append({
                        "nombre": food["description"].title(),
                        "calorias": nutrients.get("Energy", "No disponible"),
                        "proteinas": nutrients.get("Protein", "No disponible"),
                        "grasas": nutrients.get("Total lipid (fat)", "No disponible"),
                        "carbohidratos": nutrients.get("Carbohydrate, by difference", "No disponible")
                    })
                else:
                    resultados.append({"nombre": alimento.title(), "error": "No encontrado"})
            else:
                resultados.append({"nombre": alimento.title(), "error": "Error en la búsqueda"})
        except requests.exceptions.RequestException:
            resultados.append({"nombre": alimento.title(), "error": "Error de conexión"})

    return render_template('food.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    imc = None
    categoria = None

    if request.method == 'POST':
        peso = float(request.form.get('peso'))
        estatura = float(request.form.get('estatura')) / 100

        imc = round(peso / (estatura ** 2), 2)

        if imc < 18.5:
            categoria = "Bajo peso"
        elif 18.5 <= imc < 24.9:
            categoria = "Normal"
        elif 25 <= imc < 29.9:
            categoria = "Sobrepeso"
        else:
            categoria = "Obesidad"

    return render_template('calculadora.html', usuario=session['usuario'], imc=imc, categoria=categoria)
@app.route("/basal", methods=["GET", "POST"])
def basal():
    resultado = None

    if request.method == "POST":
        sexo = request.form["sexo"]
        peso = float(request.form["peso"])
        altura = float(request.form["altura"])
        edad = float(request.form["edad"])
        actividad = float(request.form["actividad"])

        if sexo == "M":
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

        calorias = tmb * actividad

        resultado = {
            "tmb": round(tmb),
            "calorias": round(calorias)
        }

    return render_template("basal.html", resultado=resultado)

plan_deficit = [
    {"nombre": "Ensalada de pollo con verduras frescas", "descripcion": "Alta en proteína, baja en calorías. Ideal para cenar sin sentir pesadez."},
    {"nombre": "Avena fría (overnight oats)", "descripcion": "Aporta fibra y saciedad por horas. Perfecta para control del apetito."},
    {"nombre": "Tostadas integrales con aguacate", "descripcion": "Rápidas, nutritivas y con grasas saludables."},
    {"nombre": "Crema de verduras sin crema", "descripcion": "Solo verduras licuadas, especias y caldo. Llenadora con pocas calorías."}
]

plan_mantenimiento = [
    {"nombre": "Bowl balanceado: arroz + verduras + pollo", "descripcion": "Proporción ideal para mantener peso y energía durante el día."},
    {"nombre": "Sándwich integral de atún", "descripcion": "Rápido, con proteína y carbohidratos balanceados."},
    {"nombre": "Huevos con espinacas y pan integral", "descripcion": "Desayuno equilibrado, fácil y delicioso."},
    {"nombre": "Ensalada de frutas con yogur natural", "descripcion": "Fresca, ligera y con probióticos para digestión saludable."}
]

plan_superavit = [
    {"nombre": "Pasta con pollo en salsa ligera", "descripcion": "Perfecta para ganar masa muscular sin excederte en grasas."},
    {"nombre": "Smoothie hipercalórico", "descripcion": "Plátano + avena + crema de cacahuate + leche. Mucha energía en un vaso."},
    {"nombre": "Arroz con huevo y aguacate", "descripcion": "Carbohidratos + proteína + grasas saludables."},
    {"nombre": "Panqué de avena y plátano", "descripcion": "Ideal como snack para aumentar calorías sin comida chatarra."}
]

@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        plan_seleccionado = request.form.get('plan')

        if plan_seleccionado == "deficit":
            plan = plan_deficit
        elif plan_seleccionado == "mantenimiento":
            plan = plan_mantenimiento
        elif plan_seleccionado == "superavit":
            plan = plan_superavit
        else:
            plan = None

        return render_template('plan.html', usuario=session['usuario'], plan=plan)

    return render_template('plan.html', usuario=session['usuario'], plan=None)
@app.route('/articulos')
def articulos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('articulos.html', usuario=session['usuario'])

@app.route("/ejercicios")
def ejercicios():
    nivel = request.args.get("nivel")

    ejercicios_dict = {
        "ligero": [
            "10 minutos de estiramientos.",
            "Caminata ligera 15 minutos.",
            "Respiración diafragmática 5 minutos."
        ],
        "moderado": [
            "20 sentadillas.",
            "15 minutos de cuerda o saltos.",
            "3 series de 12 abdominales."
        ],
        "fuerte": [
            "Burpees 3×15.",
            "Plancha 1 minuto (3 veces).",
            "Zancadas 3×20 por pierna."
        ]
    }

    ejercicios = ejercicios_dict.get(nivel, None)

    return render_template("ejercicios.html", ejercicios=ejercicios)

@app.route("/consejo", methods=["GET", "POST"])
def consejo():
    consejos = [
        "Hoy es un buen día para avanzar un poquito más.",
        "No te compares, cada proceso es único.",
        "Tu constancia vale más que tu perfección.",
        "Aliméntate para nutrir tu cuerpo, no para castigarlo.",
        "Un pequeño paso diario es mejor que ninguno.",
        "Escucha a tu cuerpo, él siempre sabe lo que necesita.",
        "Descansar también es progresar.",
        "No tienes que hacerlo perfecto, solo hacerlo.",
        "Tu cuerpo merece amor, paciencia y respeto.",
        "No te rindas, lo estás haciendo increíble."
    ]

    consejo_aleatorio = random.choice(consejos)
    return render_template("consejo.html", consejo=consejo_aleatorio)


@app.route('/gct', methods=['GET', 'POST'])
def gct():
    resultado = None
    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        edad = int(request.form['edad'])
        sexo = request.form['sexo']
        actividad = float(request.form['actividad'])

        if sexo == 'hombre':
            tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
        else:
            tmb = 10 * peso + 6.25 * altura - 5 * edad - 161

        gct_total = tmb * actividad
        resultado = round(gct_total, 2)

    return render_template('gct.html', resultado=resultado)

@app.route('/pesoideal', methods=['GET', 'POST'])
def pesoideal():
    resultado = None
    if request.method == 'POST':
        altura_cm = float(request.form['altura'])
        altura_m = altura_cm / 100
        imc_min = 18.5
        imc_max = 24.9
        peso_min = round(imc_min * altura_m**2, 2)
        peso_max = round(imc_max * altura_m**2, 2)
        resultado = f"{peso_min} - {peso_max} kg"

    return render_template('pesoideal.html', resultado=resultado)

@app.route('/macronutrintes', methods=['GET', 'POST'])
def macronutrintes():
    resultado = None
    if request.method == 'POST':
        calorias = float(request.form['calorias'])
        proteina_pct = float(request.form['proteina']) / 100
        grasa_pct = float(request.form['grasa']) / 100
        carbo_pct = float(request.form['carbo']) / 100

        proteina_g = round((calorias * proteina_pct) / 4, 2)
        grasa_g = round((calorias * grasa_pct) / 9, 2)
        carbo_g = round((calorias * carbo_pct) / 4, 2)
        resultado = f"Proteínas: {proteina_g} g, Grasas: {grasa_g} g, Carbohidratos: {carbo_g} g"

    return render_template('macronutrintes.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)