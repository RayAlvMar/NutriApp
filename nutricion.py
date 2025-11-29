from flask import Flask, render_template, request, flash, redirect, url_for, session
import random
import requests

app = Flask(__name__)
app.secret_key = 'secretishimo'

usuarios = {}

API_KEY = "0zYsgNsAc070fgtRWyul1pOkENLlfu32g3alFq3a"
API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

@app.route('/')
def home():
    return redirect(url_for('diseno'))

@app.route('/login') 
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

@app.route('/diseno')
def diseno():
  return render_template('diseno.html')


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():

    email = session['usuario']
    if email not in usuarios:
        usuarios[email] = {}

    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        edad = request.form.get('edad', '')
        estatura = request.form.get('estatura', '')
        peso = request.form.get('peso', '')
        nivel_entrenamiento = request.form.get('nivel_entrenamiento', '')
        objetivo = request.form.get('objetivo', '')

        usuarios[email]['nombre'] = nombre
        usuarios[email]['edad'] = edad
        usuarios[email]['estatura'] = estatura
        usuarios[email]['peso'] = peso
        usuarios[email]['nivel_entrenamiento'] = nivel_entrenamiento
        usuarios[email]['objetivo'] = objetivo

        session['nombre'] = nombre
        session['edad'] = edad
        session['estatura'] = estatura
        session['peso'] = peso
        session['nivel_entrenamiento'] = nivel_entrenamiento
        session['objetivo'] = objetivo

        return render_template(
            'perfil.html',
            usuario=email,
            nombre=nombre,
            edad=edad,
            estatura=estatura,
            peso=peso,
            nivel_entrenamiento=nivel_entrenamiento,
            objetivo=objetivo)

    return render_template(
        'perfil.html',
        usuario=email,
        nombre=session.get('nombre', ''),
        edad=session.get('edad', ''),
        estatura=session.get('estatura', ''),
        peso=session.get('peso', ''),
        nivel_entrenamiento=session.get('nivel_entrenamiento', ''),
        objetivo=session.get('objetivo', ''))

@app.route('/analizador', methods=['GET', 'POST'])
def analizador():
    if request.method == 'GET':
        return render_template('analizador.html')

    alimentos = request.form.get('alimentos', '').strip()
    if not alimentos:
        flash('Por favor ingresa uno o varios alimentos.', 'error')
        return redirect(url_for('analizador'))

    lista_alimentos = [a.strip() for a in alimentos.split(',') if a.strip()]
    if len(lista_alimentos) > 5:
        flash('Solo puedes buscar hasta 5 alimentos.', 'error')
        return redirect(url_for('analizador'))

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

    return render_template('resultados.html', resultados=resultados)

@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():

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

    return render_template('calculadora.html', imc=imc, categoria=categoria)

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

        return render_template('plan.html', plan=plan)

    return render_template('plan.html', plan=None)
@app.route('/articulos')
def articulos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('articulos.html')

@app.route("/ejercicios", methods=["GET", "POST"])
def ejercicios():
    if request.method == "POST":
        nivel = request.form.get("nivel")
        sexo = request.form.get("sexo")

        ejercicios_dict = {
            "ligero": {
                "hombre": [
                    {
                        "titulo": "Estiramientos dinámicos (10 minutos)",
                        "detalle": [
                            "1. Empieza de pie con los pies al ancho de hombros.",
                            "2. Realiza círculos suaves con los hombros hacia adelante 10 veces y luego hacia atrás 10 veces.",
                            "3. Balancea los brazos hacia adelante y atrás de forma controlada durante 1 minuto.",
                            "4. Haz balanceos de pierna (frontal) 10 repeticiones por pierna, mantén la espalda recta.",
                            "5. Finaliza con inclinaciones laterales del tronco: 10 por lado, respirando profundo."
                        ],
                        "consejo": "Movimientos suaves, sin rebotes, mantén respiración controlada."
                    },
                    {
                        "titulo": "Caminata a paso ligero (15 minutos)",
                        "detalle": [
                            "1. Calza tenis cómodos y comienza caminando a ritmo relajado 2 minutos.",
                            "2. Aumenta el paso hasta tener respiración ligera pero cómoda (no agitada).",
                            "3. Mantén postura erguida, brazos balanceando naturalmente.",
                            "4. Si tu pulso sube, baja ritmo 30s y vuelve a ritmo objetivo."
                        ],
                        "consejo": "Mantén hidratación y mira hacia adelante."
                    },
                    {
                        "titulo": "Respiración diafragmática (5 minutos)",
                        "detalle": [
                            "1. Siéntate cómodo o recuéstate con una mano en el pecho y otra en el abdomen.",
                            "2. Inhala por la nariz 4 segundos, siente subir la mano del abdomen.",
                            "3. Mantén 1 segundo y exhala por la boca 6 segundos.",
                            "4. Repite por 5 minutos, concentrándote en el diafragma."
                        ],
                        "consejo": "Relaja los hombros, ideal después de la caminata."
                    }
                ],
                "mujer": [
                    {
                        "titulo": "Estiramientos suaves (10 minutos)",
                        "detalle": [
                            "1. De pie, separa pies al ancho de cadera.",
                            "2. Rotaciones de cuello suaves: 5 para cada lado.",
                            "3. Estiramiento de cadera: lleva el talón al glúteo 10 veces por pierna (balanceo suave).",
                            "4. Estiramiento de espalda baja: flexión hacia adelante doblando ligeramente las rodillas, mantén 20-30s."
                        ],
                        "consejo": "No forzar, busca sensación de alivio, no dolor."
                    },
                    {
                        "titulo": "Caminata activa (15 minutos)",
                        "detalle": [
                            "1. Camina a ritmo cómodo 2 minutos para calentar.",
                            "2. Aumenta ritmo a paso firme durante 10 minutos.",
                            "3. Termina 3 minutos reduciendo ritmo para volver a la calma."
                        ],
                        "consejo": "Mantén pasos cortos si tienes molestias en rodillas."
                    },
                    {
                        "titulo": "Respiración y relajación (5 minutos)",
                        "detalle": [
                            "1. Siéntate con la espalda recta, cierra ojos.",
                            "2. Inhala 4 segundos, retén 1 segundo, exhala 6 segundos.",
                            "3. Concéntrate en relajar diafragma y hombros."
                        ],
                        "consejo": "Perfecto para bajar ansiedad o tensión."
                    }
                ]
            },
            "moderado": {
                "hombre": [
                    {
                        "titulo": "Sentadillas (3x15)",
                        "detalle": [
                            "1. Párate con pies al ancho de hombros, punta ligeramente hacia fuera.",
                            "2. Mantén la espalda recta y el pecho arriba.",
                            "3. Baja llevando las caderas hacia atrás como si te sentaras, hasta que muslos queden paralelos al suelo.",
                            "4. Empuja con talones para volver arriba. Haz 3 series de 15 repeticiones, 60-90s descanso entre series."
                        ],
                        "consejo": "No dejes que las rodillas pasen la punta de los pies."
                    },
                    {
                        "titulo": "Saltos de cuerda / jumping jacks (3x1 minuto)",
                        "detalle": [
                            "1. Salta con movimiento suave, rodillas ligeramente flexionadas.",
                            "2. Mantén muñecas ligeras controlando la cuerda o brazos si haces jumping jacks.",
                            "3. Realiza 3 series de 1 minuto con 30-45s descanso."
                        ],
                        "consejo": "Si hay impacto, haz marchas rápidas en el sitio como alternativa."
                    },
                    {
                        "titulo": "Abdominales controlados (3x20)",
                        "detalle": [
                            "1. Acuéstate boca arriba, manos detrás de la nuca o cruzadas sobre el pecho.",
                            "2. Eleva el torso usando abdominales, no tirando del cuello.",
                            "3. Baja controlado. Repite 20 veces por serie, 3 series con 45-60s descanso."
                        ],
                        "consejo": "Mantén mentón separado del pecho para evitar tensión en cuello."
                    }
                ],
                "mujer": [
                    {
                        "titulo": "Sentadillas controladas (3x12)",
                        "detalle": [
                            "1. Pies al ancho de hombros, espalda neutra.",
                            "2. Baja controlando el movimiento hasta 90 grados si puedes.",
                            "3. Sube empujando con talones. 3 series de 12, 60s descanso."
                        ],
                        "consejo": "Haz un calentamiento ligero antes con 1-2 minutos de caminata."
                    },
                    {
                        "titulo": "Elevaciones de rodillas (3x1 minuto)",
                        "detalle": [
                            "1. Marcha rápida en el sitio elevando rodillas a la altura cómoda.",
                            "2. Mantén el core contraído y la espalda recta.",
                            "3. 3 series de 1 minuto, 30s descanso."
                        ],
                        "consejo": "Buen ejercicio cardio con bajo impacto."
                    },
                    {
                        "titulo": "Abdominales básicos (3x15)",
                        "detalle": [
                            "1. Acostada boca arriba, piernas flexionadas y pies apoyados.",
                            "2. Eleva ligeramente el torso manteniendo abdomen apretado.",
                            "3. Realiza 15 repeticiones por serie, 3 series, 45-60s descanso."
                        ],
                        "consejo": "Concéntrate en la respiración: exhala al subir."
                    }
                ]
            },
            "fuerte": {
                "hombre": [
                    {
                        "titulo": "Burpees intensos (4x15)",
                        "detalle": [
                            "1. Desde pie, baja a cuclillas y coloca las manos en el suelo.",
                            "2. Salta los pies hacia atrás hasta posición de plancha.",
                            "3. Haz un push-up (opcional si no puedes, omítelo) y vuelve a saltar los pies hacia adelante.",
                            "4. Levántate y salta explosivamente con manos arriba. Repite 15 repeticiones por serie, 4 series con 60-90s descanso."
                        ],
                        "consejo": "Mantén ritmo constante; baja la intensidad si te falta respiración."
                    },
                    {
                        "titulo": "Plancha (3x1 minuto)",
                        "detalle": [
                            "1. Colócate en posición de plancha frontal con antebrazos apoyados y cuerpo recto.",
                            "2. Mantén abdomen y glúteos contraídos, evita hundir la cadera.",
                            "3. Mantén 60 segundos, descansa 45-60s, repite 3 veces."
                        ],
                        "consejo": "Si 1 minuto es mucho, empieza con 3x30s e incrementa."
                    },
                    {
                        "titulo": "Zancadas explosivas (3x20 por pierna)",
                        "detalle": [
                            "1. Da un paso largo hacia adelante y baja hasta que la rodilla trasera quede cerca del suelo.",
                            "2. Empuja hacia arriba con la pierna delantera y cambia de pierna en el aire (si haces explosivas).",
                            "3. Realiza 3 series de 20 repeticiones por pierna, 90s descanso."
                        ],
                        "consejo": "Mantén rodilla alineada con el pie y tronco erguido."
                    }
                ],
                "mujer": [
                    {
                        "titulo": "Burpees controlados (3x12)",
                        "detalle": [
                            "1. Comienza de pie, baja a cuclillas y apoya manos en el suelo.",
                            "2. Lleva pies atrás suavemente hasta plancha, evita salto brusco.",
                            "3. Vuelve a posición de cuclillas y levántate con salto ligero. 3 series de 12 repeticiones."
                        ],
                        "consejo": "Controla el ritmo si hay molestias en rodillas o espalda baja."
                    },
                    {
                        "titulo": "Plancha isométrica (3x45s)",
                        "detalle": [
                            "1. Posición de plancha con antebrazos apoyados y cuerpo recto.",
                            "2. Contrae abdomen y glúteos, evita subir la cadera.",
                            "3. Mantén 45 segundos por ronda, 60s descanso entre rondas."
                        ],
                        "consejo": "Si sientes dolor lumbar, baja el tiempo o apoya rodillas."
                    },
                    {
                        "titulo": "Zancadas estáticas (3x15 por pierna)",
                        "detalle": [
                            "1. Sitúate con un pie adelante y otro atrás (pequeña separación).",
                            "2. Baja la cadera hasta que la rodilla trasera casi toque el suelo.",
                            "3. Sube controlado sin empujar con la espalda. 3 series de 15 repeticiones por pierna."
                        ],
                        "consejo": "Mantén mirada al frente y torso estable."
                    }
                ]
            }
        }

        rutinas = ejercicios_dict.get(nivel, {}).get(sexo, None)

        return render_template("ejercicios.html",
                               rutinas=rutinas,
                               nivel=nivel,
                               sexo=sexo)
    else:
        return render_template("ejercicios.html")

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