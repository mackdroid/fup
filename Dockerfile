FROM python:3.11 as python-base
ENV APP_PATH = ./fup
WORKDIR ${APP_PATH}
COPY /pyproject.toml ${APP_PATH}
RUN pip3 install poetry==1.5.1
RUN poetry config virtualenvs.create false
RUN poetry install 
COPY . .
CMD ["poetry", "run", "gunicorn", "--workers", "1", "wsgi:app", "-t", "180", "--bind", "127.0.0.1:8001"]