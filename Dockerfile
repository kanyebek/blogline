FROM python:3.11-slim
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]