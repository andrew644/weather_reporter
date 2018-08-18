FROM resin/raspberry-pi-python:3.6

WORKDIR /usr/src/app
COPY requirements.txt .
COPY main.py .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

