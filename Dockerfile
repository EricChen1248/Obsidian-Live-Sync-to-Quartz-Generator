FROM alpine:3.22.1

RUN apk add python3 nodejs npm git py3-pip coreutils && pip3 install --break-system-packages requests dotenv
RUN git clone https://github.com/jackyzha0/quartz.git
RUN cd quartz; npm ci
COPY scripts .
COPY main.py .

ENV PYTHONUNBUFFERED=1
CMD [ "sh", "./run.sh" ]