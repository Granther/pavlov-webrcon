#syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

# ENV SECRET_KEY="xxxx"
# ENV SQLALCHEMY_DATABASE_URI="sqlite:///pavlov-rcon.db"
# ENV SERVER_IP="192.168.x.x"
# ENV SERVER_PORT=91xx
# ENV RCON_PASSWORD="xxx"
# ENV LOG_LEVEL="DEBUG"
# ENV LOGS_DIR="./logs"
# ENV ADMIN_PASSWORD="xxx"
# ENV MODIO_API_KEY="xxxxx" 

WORKDIR /pavlov-rcon
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["gunicorn", "-b" , "0.0.0.0:5010", "app:app", "--workers=1"]
