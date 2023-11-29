from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import datetime

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


class Aprobado(db.Model):
    cod_estudiante = db.Column(db.Integer, db.ForeignKey('estudiante.cod_estudiante'), primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)

    def __repr__(self):
        return '<%r Aprobado %r>' % (self.cod_estudiante,self.cod_asig)
    
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

def insert_asignatura(asignatura):
    with app.app_context():
        try:
            existing_asignatura = Asignatura.query.filter_by(cod_asig=asignatura.cod_asig).first()
            if existing_asignatura is None:
                db.session.add(asignatura)
                db.session.commit()
            else:
                print('La asignatura con el código {} ya existe, se omitirá la inserción.'.format(asignatura.cod_asig))
        except Exception as e:
            print('Hubo un problema añadiendo la asignatura: ' + str(e))
        
if __name__ == "__main__":
    bioquimica = Asignatura(cod_asig=1150,nombre="Bioquimica",unidad_creditos=3)
    insert_asignatura(bioquimica)
    morfofisiologiaI = Asignatura(cod_asig=1151,nombre="Morfofisiologia I",unidad_creditos=4)
    insert_asignatura(morfofisiologiaI)
    socioantropologia = Asignatura(cod_asig=1368,nombre="Socioantropologia",unidad_creditos=3)
    insert_asignatura(socioantropologia)
    evTendencia = Asignatura(cod_asig=1369,nombre="Evolucion y Tendencia en la Enfermeria",unidad_creditos=4)
    insert_asignatura(evTendencia)
    desPersonal = Asignatura(cod_asig=1478,nombre="Desarrollo Personal",unidad_creditos=1)
    insert_asignatura(desPersonal)
    comLengua = Asignatura(cod_asig=1479,nombre="Comunicacion y Lengua",unidad_creditos=2)
    insert_asignatura(comLengua)
    app.run(debug=True)
    