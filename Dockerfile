FROM django:onbuild
MAINTAINER m-vdb

RUN ./manage.py migrate
