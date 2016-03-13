PYTHONHOME = venv
ACTIVATE_VENV = . ${PYTHONHOME}/bin/activate
MANAGEPY = ./manage.py

default: venv deps migrate

venv:
	(test -d ${PYTHONHOME} || virtualenv --no-site-packages ${PYTHONHOME})

deps:
	${ACTIVATE_VENV} && pip install -r requirements.txt

migrate:
	${MANAGEPY} migrate

settings:
	cp env.tpl .env
