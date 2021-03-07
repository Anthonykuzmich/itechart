FROM python:3
RUN apt-get update -y && apt-get install -y build-essential
COPY . /main
WORKDIR /main
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]