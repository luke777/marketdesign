FROM python:3.9-slim-buster

WORKDIR ./app

COPY requirements.txt *.py LICENSE README.md .
COPY md md
COPY examples examples
COPY web web

RUN pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT [ "python" ]

EXPOSE 5000

CMD [ "web-solver.py" ]
