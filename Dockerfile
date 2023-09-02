FROM python:slim
RUN apt update && apt upgrade -y && apt autoremove -y && apt clean -y
RUN pip3 install -U pip
COPY . /app
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "bot.py"]