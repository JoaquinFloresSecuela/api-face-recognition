# Usa una imagen de Python con herramientas de build
FROM python:3.10-slim

# Instala dependencias necesarias para dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    && rm -rf /var/lib/apt/lists/*

# Crea carpeta de trabajo
WORKDIR /app

# Copia los archivos
COPY . .

# Instala dlib y demás dependencias
RUN pip install --upgrade pip \
    && pip install dlib==19.24.0 \
    && pip install -r requirements.txt

# Comando por defecto
CMD ["python", "api.py"]
