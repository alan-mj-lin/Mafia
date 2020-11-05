FROM tiangolo/uwsgi-nginx-flask


WORKDIR /app
COPY  . .
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV STATIC_PATH /app/mafia-react/build/static
ENV LISTEN_PORT 8000
EXPOSE 8000
ADD ./mafia.conf /etc/nginx/conf.d/
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt