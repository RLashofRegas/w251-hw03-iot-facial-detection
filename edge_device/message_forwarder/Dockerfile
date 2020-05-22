FROM alpine:edge

RUN apk update

RUN apk add mosquitto

ADD mosquitto.conf /etc/mosquitto

CMD ["/usr/sbin/mosquitto", "-v"]