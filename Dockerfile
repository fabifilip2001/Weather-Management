FROM python:3.6
COPY requirements.txt /tmp
RUN pip install -U setuptools
RUN pip install -r /tmp/requirements.txt
RUN mkdir /app
# COPY src/ /app
COPY requirements.txt /app
COPY init_db.sql /app
COPY server.py /app
WORKDIR /app
EXPOSE 6000
CMD ["python3", "server.py"]