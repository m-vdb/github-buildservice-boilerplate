FROM django:python2-onbuild
MAINTAINER m-vdb

EXPOSE 8000
CMD python manage.py migrate ; python manage.py runserver 0.0.0.0:8000
