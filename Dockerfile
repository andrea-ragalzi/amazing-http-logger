FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .

COPY ./app .

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

