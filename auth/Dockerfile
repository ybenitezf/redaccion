FROM python:3.8

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest pytest-cov && \
    pip install gunicorn
COPY . /src

CMD gunicorn "application:create_app('config.Config')" \
    --log-level=debug --reload -b 0.0.0.0:5000
