PYTHONHOME = venv
ACTIVATE_VENV = . ${PYTHONHOME}/bin/activate

default: venv deps

venv:
	(test -d ${PYTHONHOME} || virtualenv --no-site-packages ${PYTHONHOME})

deps:
	${ACTIVATE_VENV} && pip install -r requirements.txt
