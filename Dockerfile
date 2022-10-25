FROM python:3.11-alpine3.16

WORKDIR /app
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8080

CMD python main.py
