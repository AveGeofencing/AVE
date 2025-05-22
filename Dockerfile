FROM python:3.12

WORKDIR /app

ENV PORT=8080
ENV HOST=0.0.0.0

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host $HOST --port $PORT"]

