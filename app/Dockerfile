FROM python:3.8

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install -U --no-cache-dir pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest pytest-cov && \
    pip install --no-cache-dir gunicorn
COPY . /src

# remove env files
RUN rm -rf .env; rm -rf .flaskenv

CMD gunicorn "application:create_app('config.Config')" \
    --log-level=debug --reload -b 0.0.0.0:5000
