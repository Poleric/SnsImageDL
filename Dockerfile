FROM python:3.12

WORKDIR /

ARG TARGETARCH

COPY ./build_pyexiv2_on_arm.sh .

RUN if [ $TARGETARCH = "arm64" ]; then \
      ./build_pyexiv2_on_arm.sh \
    ; fi

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY media_downloader/ .
COPY bot.py .
COPY setup_logging.py .

CMD [ "python", "./bot.py"]
