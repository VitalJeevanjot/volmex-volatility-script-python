# FROM python:latest
FROM nikolaik/python-nodejs

RUN apt-get update
# RUN npm install -g nodemon

RUN \
    apt-get install -y nano && \
    apt-get install -y vim && \
    apt-get update && \
    apt-get install -y supervisor

WORKDIR /etc/supervisor/conf.d 
COPY . .
RUN pip install -r requirements.txt

RUN mkdir /var/log/webhook

# RUN supervisord -c /etc/supervisor/supervisord.conf &&\
#     supervisorctl -c /etc/supervisor/supervisord.conf &&\
#     supervisorctl reread &&\
#     supervisorctl update



# Define default command.
# CMD supervisorctl
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
EXPOSE 9001