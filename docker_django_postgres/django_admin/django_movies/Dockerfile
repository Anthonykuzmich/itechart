FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /django_movies
COPY requirements.txt /django_movies/
RUN pip install -r requirements.txt
COPY . /django_movies
EXPOSE 8000