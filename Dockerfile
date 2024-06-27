FROM python:3.12-alpine

WORKDIR /usr/src/app

ARG TARGETARCH

COPY build_pyexiv2.sh .

RUN ./build_pyexiv2.sh

RUN if [ $TARGETARCH = "arm64" ]; then \
      apk add --update --no-cache gcc libc-dev libffi-dev \
    ; fi

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bot.py"]
