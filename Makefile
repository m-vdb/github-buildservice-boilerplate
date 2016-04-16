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

lint:
	pylint buildservice --rcfile=pylint.rc
	pylint buildservice/tests --rcfile=pylint.rc --method-rgx='([a-z_][a-z0-9_]{2,50}|(setUp|tearDown)(Class)?)$$' --disable=no-member,missing-docstring,too-many-ancestors
