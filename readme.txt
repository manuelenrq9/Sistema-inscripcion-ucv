Inicializar base de datos:
Python
>>> from inscripcion import app, db
>>> app.app_context().push()
>>> db.create_all()

Ejecutar aplicación:
python inscripcion.py

Salir de la terminal de python:
exit()