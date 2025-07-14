# Containerfile
FROM tensorflow/tensorflow:latest-gpu

WORKDIR /code

# Copia requisitos e instala depencias
COPY requirements.txt /code/requirements.txt
RUN apt-get update \
 && apt-get install -y libgl1 \
 && pip install --upgrade pip \
 && pip install --no-cache-dir --upgrade --ignore-installed blinker -r /code/requirements.txt

# Copia tu aplicación
COPY app /code/app

# Directorios de datos que vas a mapear
VOLUME ["/code/data/events_imgs", "/code/data/people_imgs"]

# Expone el puerto
EXPOSE 8000

# Lanza la app con uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]