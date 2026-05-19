FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Set environment variables for Flask
ENV FLASK_APP=app:create_app
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run"]