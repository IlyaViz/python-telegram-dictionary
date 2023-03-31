FROM python:latest
RUN pip install psycopg2
RUN pip install python-telegram-bot==13.7
COPY ./ ./app
WORKDIR /app
CMD ["python", "tg_bot.py"]
