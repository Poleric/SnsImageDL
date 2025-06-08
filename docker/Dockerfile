FROM python:3.13-slim

WORKDIR /usr/src/app/

RUN pip install --no-cache-dir discord.py

COPY . .

RUN pip install --no-cache-dir -e .

CMD ["python3", "bot.py"]
