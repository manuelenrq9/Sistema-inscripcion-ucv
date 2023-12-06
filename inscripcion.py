from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


class Asignatura(db.Model):
    cod_asig = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    unidad_creditos = db.Column(db.Integer)

    def __repr__(self):
        return '<Asignatura %r>' % self.cod_asig


class Estudiante(db.Model):
    cod_estudiante = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    cedula = db.Column(db.Integer)
    nacimiento = db.Column(db.DateTime)
    telefono = db.Column(db.Integer)
    correo = db.Column(db.String(200), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    direccion = db.Column(db.String(200), nullable=False)
    forma_ingreso = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Estudiante %r>' % self.cod_estudiante
    
class Seccion(db.Model):
    cod_seccion = db.Column(db.Integer, primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'))
    capacidad = db.Column(db.Integer)
    profesor = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Seccion %r>' % self.cod_seccion

class Cursando(db.Model):
    cod_estudiante = db.Column(db.Integer, db.ForeignKey('estudiante.cod_estudiante'), primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)

    def __repr__(self):
        return '<%r Cursando  %r>' % (self.cod_estudiante, self.cod_asig)


class Calificacion(db.Model):
    cod_estudiante = db.Column(db.Integer, db.ForeignKey('estudiante.cod_estudiante'), primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)
    nota = db.Column(db.Integer)
    aprobado = db.Column(db.Boolean)
    
    def __init__(self, cod_estudiante, cod_asig, nota):
        self.cod_estudiante = cod_estudiante
        self.cod_asig = cod_asig
        self.nota = nota
        self.aprobado = self.calcular_aprobacion()

    def calcular_aprobacion(self):
        return self.nota >= 10
    
    def __repr__(self):
        return '< Calificacion de %r en %r es %r (%r)>' % (self.cod_estudiante,self.cod_asig,self.nota,self.aprobado)
    
class Requisito(db.Model):
    cod_requisito = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)

    def __repr__(self):
        return '<%r Requisito de %r>' % (self.cod_requisito,self.cod_asig)

@app.route('/', methods=['POST', 'GET'])
def index():
        return render_template('menu_principal.html')

@app.route('/nuevo_ingreso', methods=['POST','GET'])
def nuevoIngreso():
    if request.method == 'POST':
        nombre = request.form['NOMBRE']
        cedula = request.form['CEDULA']
        nacimiento = request.form['DOB']
        nacimiento = datetime.strptime(nacimiento, '%Y-%m-%d')
        telefono = request.form['TELEFONO']
        correo = request.form['CORREO']
        direccion = request.form['DIRECCION']
        forma_ingreso = request.form['INGRESO']
                
        nuevo_estudiante = Estudiante(nombre=nombre,cedula=cedula,nacimiento=nacimiento,telefono=telefono,correo=correo,direccion=direccion,forma_ingreso=forma_ingreso)
                
        try:
            db.session.add(nuevo_estudiante)
            db.session.commit()
            
            bioquimica = Cursando(cod_estudiante=nuevo_estudiante.cod_estudiante,cod_asig=1150)
            morfofisiologiaI = Cursando(cod_estudiante=nuevo_estudiante.cod_estudiante,cod_asig=1151)
            socioantropologia = Cursando(cod_estudiante=nuevo_estudiante.cod_estudiante,cod_asig=1368)
            evTendencia = Cursando(cod_estudiante=nuevo_estudiante.cod_estudiante,cod_asig=1369)
            desPersonal = Cursando(cod_estudiante=nuevo_estudiante.cod_estudiante,cod_asig=1478)
            comLengua = Cursando(cod_estudiante=nuevo_estudiante.cod_estudiante,cod_asig=1479)
            
            db.session.add_all([bioquimica, morfofisiologiaI, socioantropologia,evTendencia,desPersonal,comLengua])
            db.session.commit()
            
            return redirect('/')
        except Exception as e:
             print(e)
             return 'Hubo un problema añadiendo al estudiante: ' + str(e)
    else:
        return render_template('nuevoingreso.html')
    
@app.route('/asignatura', methods=['POST','GET'])
def asignatura_nueva():
    if request.method == 'POST':
        cod_asig = request.form['CODIGO']
        nombre = request.form['NOMBRE']
        unidad_creditos = request.form['CREDITOS']
                
        nueva_asignatura = Asignatura(cod_asig=cod_asig,nombre=nombre,unidad_creditos=unidad_creditos)
                
        try:
            db.session.add(nueva_asignatura)
            db.session.commit()
            return redirect('/')
        except Exception as e:
             print(e)
             return 'Hubo un problema añadiendo la asignatura: ' + str(e)
    else:
        return render_template('asignatura.html')
    
@app.route('/estudiantes', methods=['GET', 'POST'])
def listar_estudiantes():
    if request.method == 'POST':
        pass
    else:
        estudiantes = Estudiante.query.all()
        return render_template('estudiantes.html', estudiantes=estudiantes)
    
@app.route('/info_estudiante/<int:id>', methods=['GET', 'POST'])
def info_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    cursando = Cursando.query.filter_by(cod_estudiante=estudiante.cod_estudiante).all()
    codigos_asignaturas = [curso.cod_asig for curso in cursando]
    asignaturas = Asignatura.query.filter(Asignatura.cod_asig.in_(codigos_asignaturas)).all()
    if request.method == 'POST':
        pass
    else:
        # Consulta para obtener solo los registros de asignaturas que esté cursando el estudiante
        return render_template('info_estudiante.html', asignaturas=asignaturas, estudiante=estudiante)

@app.route('/asignaturas_notas', methods=['GET', 'POST'])
def listar_asignaturas():
    if request.method == 'POST':
        pass
    else:
        asignaturas = Asignatura.query.all()
        return render_template('asignaturas_notas.html', asignaturas=asignaturas)
    
@app.route('/estudiantes_notas/<int:id>', methods=['GET', 'POST'])
def listar_estudiantes_notas(id):
    asignatura = Asignatura.query.get_or_404(id)
    
    cursando = Cursando.query.filter_by(cod_asig=asignatura.cod_asig).all()
    codigos_estudiantes = [cursando.cod_estudiante for cursando in cursando]
    estudiantes = Estudiante.query.filter(Estudiante.cod_estudiante.in_(codigos_estudiantes)).all()
    if request.method == 'POST':
        pass
    else:
        return render_template('estudiantes_notas.html', estudiantes=estudiantes, asignatura = asignatura)
    
@app.route('/carga_notas/<int:idEst>/<int:idAsig>', methods=['GET', 'POST'])
def cargar_nota(idEst,idAsig):
    estudiante =  Estudiante.query.get_or_404(idEst)
    asignatura = Asignatura.query.get_or_404(idAsig)
    cursando = Cursando.query.filter_by(cod_estudiante=estudiante.cod_estudiante, cod_asig=asignatura.cod_asig).first()
    if request.method == 'POST':
        nota = int(request.form['CARGA'])
        calificacion = Calificacion(idEst,idAsig,nota)
        try:
            db.session.add(calificacion)
            db.session.commit()
            db.session.delete(cursando)
            db.session.commit()
            return redirect('/')
        except Exception as e:
             print(e)
             return 'Hubo un problema actualizando la calificación: ' + str(e)
       
    else:
        return render_template('cargar_notas.html', estudiante=estudiante, asignatura=asignatura)
    
@app.route('/busqueda_regular', methods=['GET', 'POST','INSCRIBIR'])
def buscar_regular():
    estudiante = None
    if request.method == 'POST':
        cedula = request.form['CEDULA']
        estudiante = Estudiante.query.filter_by(cedula=cedula).first_or_404(description="Estudiante no encontrado")
        return render_template('busqueda_regular.html', estudiante=estudiante)        
    else:
        return render_template('busqueda_regular.html', estudiante = estudiante)
    
@app.route('/inscripcion_regular/<int:id>', methods=['GET', 'POST'])
def inscribir_regular(id):
    mensaje = ''
    estudiante = Estudiante.query.get_or_404(id)
    # Obtener las calificaciones aprobadas
    aprobados = Calificacion.query.filter_by(aprobado=True).all()
        
    # Obtener los códigos de asignatura de las calificaciones aprobadas
    codigos_aprobados = [calificacion.cod_asig for calificacion in aprobados]

    # Obtener los códigos de asignatura cuyos requisitos estén aprobados
    requisitos_aprobados = Requisito.query.filter(Requisito.cod_requisito.in_(codigos_aprobados)).all()
    codigos_requisitos = [codigo.cod_asig for codigo in requisitos_aprobados]
    
    #Obtener los codigos de asignatura de las asignaturas que el estudiante este cursando 
    cursando =  Cursando.query.filter_by(cod_estudiante=estudiante.cod_estudiante).all()
    codigos_cursando = [codigo.cod_asig for codigo in cursando]

    # Obtener las asignaturas cuyos códigos estén en codigos_requisitos_aprobados y que no estén en codigos_aprobados
    asignaturas = Asignatura.query.filter(and_(Asignatura.cod_asig.in_(codigos_requisitos), ~Asignatura.cod_asig.in_(codigos_aprobados), ~Asignatura.cod_asig.in_(codigos_cursando))).all()
    if request.method == 'POST':
        cod_asignatura = request.form['ASIGNATURA']
        cod_asignatura = int(cod_asignatura)
        asignatura_cod = [codigo.cod_asig for codigo in asignaturas]
        if (cod_asignatura in asignatura_cod):
            regular_cursando = Cursando(cod_estudiante=estudiante.cod_estudiante,cod_asig=cod_asignatura)  
            print(regular_cursando)  
            try:
                db.session.add(regular_cursando)
                db.session.commit()
                # Obtener las calificaciones aprobadas
                aprobados = Calificacion.query.filter_by(aprobado=True).all()
        
                # Obtener los códigos de asignatura de las calificaciones aprobadas
                codigos_aprobados = [calificacion.cod_asig for calificacion in aprobados]

                # Obtener los códigos de asignatura cuyos requisitos estén aprobados
                requisitos_aprobados = Requisito.query.filter(Requisito.cod_requisito.in_(codigos_aprobados)).all()
                codigos_requisitos = [codigo.cod_asig for codigo in requisitos_aprobados]
                
                #Obtener los codigos de asignatura de las asignaturas que el estudiante este cursando 
                cursando =  Cursando.query.filter_by(cod_estudiante=estudiante.cod_estudiante).all()
                codigos_cursando = [codigo.cod_asig for codigo in cursando]
               
               
                asignaturas = Asignatura.query.filter(and_(Asignatura.cod_asig.in_(codigos_requisitos), ~Asignatura.cod_asig.in_(codigos_aprobados), ~Asignatura.cod_asig.in_(codigos_cursando))).all()
                mensaje='Asignatura inscrita correctamente'
                return render_template('inscripcion_regular.html', estudiante=estudiante, asignaturas=asignaturas,mensaje=mensaje)
            
            except Exception as e:
                mensaje='No se pudo inscribir la asignatura solicitada'
                return render_template('inscripcion_regular.html', estudiante=estudiante, asignaturas=asignaturas,mensaje=mensaje)   
        else:
            mensaje='No se pudo inscribir la asignatura solicitada'
            return render_template('inscripcion_regular.html', estudiante=estudiante, asignaturas=asignaturas,mensaje=mensaje)
    else:
        return render_template('inscripcion_regular.html', estudiante=estudiante, asignaturas=asignaturas,mensaje=mensaje)




@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
       return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)
    
def insert_estudiantes_from_excel(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    print(df) 
    # Iterate through the rows and insert the data into the database
    for index, row in df.iterrows():
        nombre = row['Nombre']
        cedula = row['Cedula']
        nacimiento = row['Nacimiento']
        telefono = row['Telefono']
        correo = row['Correo']
        direccion = row['Direccion']
        forma_ingreso = row['Forma_ingreso']
        # Add other columns as needed
        nuevo_estudiante = Estudiante(nombre=nombre, cedula=cedula, nacimiento=nacimiento, telefono=telefono, correo=correo, fecha_inscripcion=datetime.utcnow(), direccion=direccion, forma_ingreso=forma_ingreso) # Add other columns as needed
        with app.app_context():
            db.session.add(nuevo_estudiante)
            db.session.commit()

def insert_asignatura(asignatura):
    with app.app_context():
        try:
            existing_asignatura = Asignatura.query.filter_by(cod_asig=asignatura.cod_asig).first()
            if existing_asignatura is None:
                db.session.add(asignatura)
                db.session.commit()
            else:
                print('')
        except Exception as e:
            print('Hubo un problema añadiendo la asignatura: ' + str(e))
            
def insert_requisito(requisito):
    with app.app_context():
        try:
            existing_requisito = Requisito.query.filter_by(cod_requisito=requisito.cod_requisito, cod_asig=requisito.cod_asig).first()
            if existing_requisito is None:
                db.session.add(requisito)
                db.session.commit()
            else:
                print('')
        except Exception as e:
            print('Hubo un problema añadiendo la asignatura: ' + str(e))
        
def asignaturas_enfermeria():
    ##  PRIMER SEMESTRE  ##
    bioquimica = Asignatura(cod_asig=1150,nombre="Bioquímica",unidad_creditos=3)
    insert_asignatura(bioquimica)
    morfofisiologiaI = Asignatura(cod_asig=1151,nombre="Morfofisiología I",unidad_creditos=4)
    insert_asignatura(morfofisiologiaI)
    socioantropologia = Asignatura(cod_asig=1368,nombre="Socioantropología",unidad_creditos=3)
    insert_asignatura(socioantropologia)
    evTendencia = Asignatura(cod_asig=1369,nombre="Evolución y Tendencia en la Enfermería",unidad_creditos=4)
    insert_asignatura(evTendencia)
    desPersonal = Asignatura(cod_asig=1478,nombre="Desarrollo Personal",unidad_creditos=1)
    insert_asignatura(desPersonal)
    comLengua = Asignatura(cod_asig=1479,nombre="Comunicación y Lengua",unidad_creditos=2)
    insert_asignatura(comLengua)
    
    ##  SEGUNDO SEMESTRE  ##
    micro =  Asignatura(cod_asig=2152,nombre="Microbiología",unidad_creditos=3)
    insert_asignatura(micro)
    morfoII = Asignatura(cod_asig=2153,nombre="Morfofisiología II",unidad_creditos=4)
    insert_asignatura(morfoII)
    enf_basica = Asignatura(cod_asig=2256,nombre="Enfermería Básica",unidad_creditos=8)
    insert_asignatura(enf_basica)
    meto_estadistica = Asignatura(cod_asig=2370,nombre="Metodología Estadística",unidad_creditos=2)
    insert_asignatura(meto_estadistica)
    psico_general = Asignatura(cod_asig=2480,nombre="Psicología General",unidad_creditos=2)
    insert_asignatura(psico_general)
    
    ##  TERCER SEMESTRE  ##
    fisio = Asignatura(cod_asig=3154,nombre="Fisiopatología",unidad_creditos=3)
    insert_asignatura(fisio)
    farmaco = Asignatura(cod_asig=3155,nombre="Farmacología",unidad_creditos=4)
    insert_asignatura(farmaco)
    enf_medica = Asignatura(cod_asig=3257,nombre="Enfermería Médica",unidad_creditos=10)
    insert_asignatura(enf_medica)
    bio_epi = Asignatura(cod_asig=3373,nombre="Bioestadística y Epidemiología",unidad_creditos=3)
    insert_asignatura(bio_epi)
    inglesI = Asignatura(cod_asig=3481, nombre="Inglés I",unidad_creditos=2)
    insert_asignatura(inglesI)
    
    ##  CUARTO SEMESTRE  ##
    mental_psiquiatria = Asignatura(cod_asig=4258,nombre="Enfermería Salud Mental y Psquiatría",unidad_creditos=9)
    insert_asignatura(mental_psiquiatria)
    meto_investigacion = Asignatura(cod_asig=4371,nombre="Metodología de Investigación",unidad_creditos=3)
    insert_asignatura(meto_investigacion)
    materno1 = Asignatura(cod_asig=4372,nombre="Enfermería Materno Infantil Atención Comunitaria I",unidad_creditos=10)
    insert_asignatura(materno1)
    inglesII = Asignatura(cod_asig=4482,nombre="Inglés Instrumental II",unidad_creditos=2)
    insert_asignatura(inglesII)
    
    ##  QUINTO SEMESTRE  ##
    enf_quirurgica = Asignatura(cod_asig=5259,nombre="Enfermería Quirúrgica",unidad_creditos=10)
    insert_asignatura(enf_quirurgica)
    materno2 = Asignatura(cod_asig=5374,nombre="Enfermería Materno Infantil y Atención Comunitaria II",unidad_creditos=9)
    insert_asignatura(materno2)
    admi_atencion_enf = Asignatura(cod_asig=5375,nombre="Administración de la Atencion de Enfermería",unidad_creditos=4)
    insert_asignatura(admi_atencion_enf)
    
    ##  SEXTO SEMESTRE  ##
    internado = Asignatura(cod_asig=6260,nombre="Internado Rotatorio",unidad_creditos=10)
    insert_asignatura(internado)
    servicio_comu = Asignatura(cod_asig=6376,nombre="Servicio Comunitario",unidad_creditos=0)
    insert_asignatura(servicio_comu)
    
    ##  SEPTIMO SEMESTRE  ##
    area_critica = Asignatura(cod_asig=7261,nombre="Concentración Clínica de Enfermería Área Crítica",unidad_creditos=18)
    insert_asignatura(area_critica)
    etica = Asignatura(cod_asig=7264,nombre="Ética en Enfermería - Electiva I",unidad_creditos=4)
    insert_asignatura(etica)
    nutricion =  Asignatura(cod_asig=7283,nombre="Nutrición en Enfermería - Electiva I",unidad_creditos=4)
    insert_asignatura(nutricion)
    
    ##  OCTAVO SEMESTRE  ##
    geriatria =  Asignatura(cod_asig=8262,nombre="Geriatría y Gerontología - Electiva II",unidad_creditos=4)
    insert_asignatura(geriatria)
    salud_ocupa = Asignatura(cod_asig=8385,nombre="Salud Ocupacional - Electiva II",unidad_creditos=4)
    insert_asignatura(salud_ocupa)
    seminario =  Asignatura(cod_asig=8263,nombre="Seminario Taller en Enfermería",unidad_creditos=9)
    insert_asignatura(seminario)
    inv_aplicadaI = Asignatura(cod_asig=8265,nombre="Investigación Aplicada área Enfermería I",unidad_creditos=7)
    insert_asignatura(inv_aplicadaI)
    
    ##  NOVENO SEMESTRE  ##
    inv_aplicadaII = Asignatura(cod_asig=9266,nombre="Investigación Aplicada en Enfermería II",unidad_creditos=6)
    insert_asignatura(inv_aplicadaII)
    enf_comunitaria = Asignatura(cod_asig=9376,nombre="Enfermería Comunitaria III",unidad_creditos=9)
    insert_asignatura(enf_comunitaria)
    admi_servicios = Asignatura(cod_asig=9377,nombre="Administración de los Servicios de Enfermería",unidad_creditos=9)
    insert_asignatura(admi_servicios)
    
    ##  DECIMO SEMESTRE  ##
    pasantia = Asignatura(cod_asig=100267,nombre="Pasantías por áreas de Interes",unidad_creditos=10)
    insert_asignatura(pasantia)
    teg = Asignatura(cod_asig=100268,nombre="Trabajo Especial de Grado",unidad_creditos=0)
    insert_asignatura(teg)
    
    
       
def requisitos_enfermeria():
    #Segundo Semestre
    micro_1 = Requisito(cod_requisito=1150,cod_asig=2152)
    insert_requisito(micro_1) 
    morfoII_1 = Requisito(cod_requisito=1150, cod_asig=2153)
    insert_requisito(morfoII_1)
    morfoII_2 = Requisito(cod_requisito=1151, cod_asig=2153)
    insert_requisito(morfoII_2)
    enfBasica_1 = Requisito(cod_requisito=1150, cod_asig=2256)
    insert_requisito(enfBasica_1)
    enfBasica_2 = Requisito(cod_requisito=1151, cod_asig=2256)
    insert_requisito(enfBasica_2)
    enfBasica_3 = Requisito(cod_requisito=1369, cod_asig=2256)
    insert_requisito(enfBasica_3)
    metodoEst_1 = Requisito(cod_requisito=1369, cod_asig=2370)
    insert_requisito(metodoEst_1)
    metodoEst_2 = Requisito(cod_requisito=1150, cod_asig=2370)
    insert_requisito(metodoEst_2)
    metodoEst_3 = Requisito(cod_requisito=1368, cod_asig=2370)
    insert_requisito(metodoEst_3)
    psicoGeneral = Requisito(cod_requisito=1478,cod_asig=2480)
    insert_requisito(psicoGeneral)
    
    #Tercer Semestre
    fisio = Requisito(cod_requisito=2153,cod_asig=3154)
    insert_requisito(fisio)
    #farmaco_1 = Requisito(cod_requisito=1150,cod_asig=3155)
    #insert_requisito(farmaco_1)
    #farmaco_2 = Requisito(cod_requisito=1151,cod_asig=3155)
    #insert_requisito(farmaco_2)
    farmaco_3 = Requisito(cod_requisito=2153,cod_asig=3155)
    insert_requisito(farmaco_3)
    EnfMedica= Requisito(cod_requisito=2256,cod_asig=3257)
    insert_requisito(EnfMedica)
    bioEpi= Requisito(cod_requisito=2370,cod_asig=3373)
    insert_requisito(bioEpi)
    #inglesI_1= Requisito(cod_requisito=1479,cod_asig=3481)
    #insert_requisito(inglesI_1)
    inglesI_2= Requisito(cod_requisito=2370,cod_asig=3481)
    insert_requisito(inglesI_2)
    
    #Cuarto Semestre
    mentalyPsiq= Requisito(cod_requisito=3257,cod_asig=4258)
    insert_requisito(mentalyPsiq)
    #metodInv= Requisito(cod_requisito=2370,cod_asig=4371)
    #insert_requisito(metodInv)
    metodInv_1= Requisito(cod_requisito=3257,cod_asig=4371)
    insert_requisito(metodInv_1)
    maternoI= Requisito(cod_requisito=3257,cod_asig=4372)
    insert_requisito(maternoI)
    inglesII= Requisito(cod_requisito=3481,cod_asig=4482)
    insert_requisito(inglesII)
    
    #Quinto Semestre
    #enfQuirur_1= Requisito(cod_requisito=3257,cod_asig=5259)
    #insert_requisito(enfQuirur_1)
    enfQuirur_2= Requisito(cod_requisito=4258,cod_asig=5259)
    insert_requisito(enfQuirur_2)
    enfQuirur_3= Requisito(cod_requisito=4372,cod_asig=5259)
    insert_requisito(enfQuirur_3)
    maternoII_1= Requisito(cod_requisito=4258,cod_asig=5374)
    insert_requisito(maternoII_1)
    maternoII_2= Requisito(cod_requisito=4372,cod_asig=5374)
    insert_requisito(maternoII_2)
    #adminEnf_1= Requisito(cod_requisito=3257,cod_asig=5375)
    #insert_requisito(adminEnf_1)
    adminEnf_2= Requisito(cod_requisito=4258,cod_asig=5375)
    insert_requisito(adminEnf_2)
    adminEnf_3= Requisito(cod_requisito=4372,cod_asig=5375)
    insert_requisito(adminEnf_3)
    
    #Sexto Semestre
    #interRot_1= Requisito(cod_requisito=3373,cod_asig=6260)
    #insert_requisito(interRot_1)
    #interRot_2= Requisito(cod_requisito=4258,cod_asig=6260)
    #insert_requisito(interRot_2)
    #interRot_3= Requisito(cod_requisito=4371,cod_asig=6260)
    #insert_requisito(interRot_3)
    #interRot_4= Requisito(cod_requisito=4372,cod_asig=6260)
    #insert_requisito(interRot_4)
    interRot_5= Requisito(cod_requisito=5259,cod_asig=6260)
    insert_requisito(interRot_5)
    interRot_6= Requisito(cod_requisito=5374,cod_asig=6260)
    insert_requisito(interRot_6)
    #servCom_1= Requisito(cod_requisito=3373,cod_asig=6261)
    #insert_requisito(servCom_1)
    #servCom_2= Requisito(cod_requisito=4258,cod_asig=6261)
    #insert_requisito(servCom_2)
    #servCom_3= Requisito(cod_requisito=4371,cod_asig=6261)
    #insert_requisito(servCom_3)
    #servCom_4= Requisito(cod_requisito=4372,cod_asig=6261)
    #insert_requisito(servCom_4)
    servCom_5= Requisito(cod_requisito=5259,cod_asig=6261)
    insert_requisito(servCom_5)
    servCom_6= Requisito(cod_requisito=5374,cod_asig=6261)
    insert_requisito(servCom_6)
    
    #Septimo Semestre
    areaCrit_1 = Requisito(cod_requisito=6260,cod_asig=7261)
    insert_requisito(areaCrit_1)
    areaCrit_2 = Requisito(cod_requisito=6261,cod_asig=7261)
    insert_requisito(areaCrit_2)
    etica_1 = Requisito(cod_requisito=6260,cod_asig=7264)
    insert_requisito(etica_1)
    etica_2 = Requisito(cod_requisito=6261,cod_asig=7264)
    insert_requisito(etica_2)
    nutricion_1 = Requisito(cod_requisito=6260,cod_asig=7283)
    insert_requisito(nutricion_1)
    nutricion_2 = Requisito(cod_requisito=6261,cod_asig=7283)
    insert_requisito(nutricion_2)
    
    #Octavo Semestre
    geriatria = Requisito(cod_requisito=7264,cod_asig=8262)
    insert_requisito(geriatria)
    seminario= Requisito(cod_requisito=7261,cod_asig=8263)
    insert_requisito(seminario) 
    invApliI = Requisito(cod_requisito=7261,cod_asig=8265)
    insert_requisito(invApliI)
    saludOcup = Requisito(cod_requisito=7283,cod_asig=8385)
    insert_requisito(saludOcup)
    
    #Noveno Semestre
    invApliII = Requisito(cod_requisito=8265,cod_asig=9265)
    insert_requisito(invApliII)
    enfComIII= Requisito(cod_requisito=8263,cod_asig=9376)
    insert_requisito(enfComIII)
    adminServ= Requisito(cod_requisito=8263,cod_asig=9377)
    insert_requisito(adminServ)
    
    #Decimo semestre
    #pasantias_1= Requisito(cod_requisito=8263,cod_asig=100267)
    #insert_requisito(pasantias_1)
    #pasantias_2= Requisito(cod_requisito=8265,cod_asig=100267)
    #insert_requisito(pasantias_2)
    pasantias_3= Requisito(cod_requisito=9265,cod_asig=100267)
    insert_requisito(pasantias_3)
    #teg_1 = Requisito(cod_requisito=8265,cod_asig=100268)
    #insert_requisito(teg_1)
    teg_2 = Requisito(cod_requisito=9265,cod_asig=100268)
    insert_requisito(teg_2)
    
if __name__ == "__main__":
    asignaturas_enfermeria()
    requisitos_enfermeria()
    est_excel = 'estudiantes.xlsx'
    print(est_excel)
    insert_estudiantes_from_excel(est_excel)
    app.run(debug=True)
    