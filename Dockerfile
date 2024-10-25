#syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

#
# ENV SECRET_KEY="gungho"
# ENV SQLALCHEMY_DATABASE_URI="sqlite:///pavlov-rcon.db"
# ENV SERVER_IP="192.168.1.195"
# ENV SERVER_PORT=9100
# ENV RCON_PASSWORD="glorp123"
# ENV LOG_LEVEL="DEBUG"
# ENV LOGS_DIR="./logs"
# ENV ADMIN_PASSWORD="Glorpav1024"
# ENV MODIO_API_KEY="8bd2faddfb0220443735c8cc4cd42727" 

WORKDIR /pavlov-rcon
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["gunicorn", "-b" , "0.0.0.0:5010", "app:app", "--workers=1"]