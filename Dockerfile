FROM python:latest
COPY ./ ./app
WORKDIR /app
RUN pip install requirements.txt
CMD ["python", "tg_bot.py"]
