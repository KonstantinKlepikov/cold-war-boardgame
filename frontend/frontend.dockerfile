FROM python:3.8.12

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY ./app /app/
WORKDIR /app/

RUN pip install -r requirements.txt

ENV API_ROOT='http://backend:8000'

ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]