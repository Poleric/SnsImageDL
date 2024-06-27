FROM python:3.12-alpine

WORKDIR /usr/src/app

ARG TARGETARCH

COPY build_pyexiv2_on_arm.sh .

RUN ./build_pyexiv2_on_arm.sh

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bot.py"]
