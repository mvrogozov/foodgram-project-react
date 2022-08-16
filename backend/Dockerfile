FROM python:3.7-slim
RUN apt-get update
#RUN mkdir /app
WORKDIR /app
COPY requirements/requirements.txt .
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY ./ .
LABEL author='mv_rogozov'
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]