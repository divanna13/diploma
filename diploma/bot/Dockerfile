
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py /app/app.py
WORKDIR /app
CMD ["python", "app.py"]
EXPOSE 3478