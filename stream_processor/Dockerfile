FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY processor.py .
# Ensure model.pkl will be available from trainer phase since we mount volumes in compose
CMD ["python", "processor.py"]
