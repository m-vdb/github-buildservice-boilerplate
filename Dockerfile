FROM django:python2-onbuild
MAINTAINER m-vdb

RUN ./manage.py migrate
