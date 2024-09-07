FROM python:3.12 AS development

WORKDIR /backend/

COPY ./requirements.txt /backend/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./song_examples /backend/song_examples

COPY ./alembic.ini /backend/

COPY ./src /backend/src

RUN alembic upgrade head

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]