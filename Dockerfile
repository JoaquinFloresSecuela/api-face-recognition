# Usa una imagen oficial con Python 3.10 o 3.9
FROM python:3.10-slim

# Actualiza el sistema e instala cmake y otras dependencias necesarias
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crea un directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala las dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expón el puerto en que corre tu app (modifica según tu app)
EXPOSE 8000

# Comando para correr tu app
CMD ["python", "api.py"]
