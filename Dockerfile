FROM python:3.9-slim-buster

WORKDIR ./app

COPY requirements.txt *.py LICENSE README.md .
COPY md md
COPY examples examples
COPY web web

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "1", "--threads",  "12"]