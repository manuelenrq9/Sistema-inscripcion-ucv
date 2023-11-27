from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
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
    cod_estudiante = db.Column(db.Integer, primary_key=True)
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
        return '<%r Cursando %r>' % self.cod_estudiante % self.cod_asig

class Aprobado(db.Model):
    cod_estudiante = db.Column(db.Integer, db.ForeignKey('estudiante.cod_estudiante'), primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)

    def __repr__(self):
        return '<%r Aprobado %r>' % self.cod_estudiante % self.cod_asig
    
class Requisito(db.Model):
    cod_requisito = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asig'), primary_key=True)

    def __repr__(self):
        return '<%r Requisito %r>' % self.cod_asig % self.cod_asig


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)




#@app.route('/inscribir_nuevo', methods=['POST', 'GET'])
#def index():
#    if request.method == 'POST':
#        task_content = request.form['content']
#        new_task = Todo(content=task_content)
#
#       try:
#            db.session.add(new_task)
#            db.session.commit()
#            return redirect('/')
#        except:
#            return 'There was an issue adding your task'
#
#    else:
#        tasks = Todo.query.order_by(Todo.date_created).all()
#        return render_template('index.html', tasks=tasks)




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


if __name__ == "__main__":
    app.run(debug=True)