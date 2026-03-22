FROM python:3.12-alpine

ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH=/home/fast \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup -S fast \
    && adduser -S fast -G fast -h "$HOME" \
    && mkdir -p "$APP_HOME" "$HOME/media/products"

WORKDIR $HOME

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini ./

RUN chown -R fast:fast "$HOME"

USER fast

EXPOSE 8000
