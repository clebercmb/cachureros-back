# cachureros-back


PYTHON<br />
Flask<br />
$ Pip install pipenv<br />
$ Python -m pip install --upgrade pip<br /><br />

#Create file Pipfile<br />
$ pipenv shell   (cria ambiente virtual)<br /><br />

$ pipenv install flask flask-sqlalchemy flask-script flask-migrate flask-cors<br /><br />

$ python src/app.py db init<br />
$ python src/app.py db migrate<br />
$ python src/app.py db upgrade<br />
$ python src/app.py runserver<br />