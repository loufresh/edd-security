FROM python:3.11-slim

WORKDIR /app

# Copia requirements primero
COPY requirements.txt .

# Instala dependencias de Python directamente
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Puerto para FastAPI
ENV PORT=8000

# Comando para arrancar la API
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
