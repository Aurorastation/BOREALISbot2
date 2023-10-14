FROM python:3.6-stretch
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV LOG_CFG logging.docker.yml
CMD ["python", "main.py"]