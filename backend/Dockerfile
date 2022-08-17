FROM python:3.7-slim
RUN apt-get update
WORKDIR /app
COPY requirements/requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY foodgram/ .
LABEL author='mv_rogozov'
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
