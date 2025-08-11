FROM ubuntu:22.04
RUN apt-get update && apt-get install -y libicu70 libpulse0 libx11-6 libnss3 libssl3 && rm -rf /var/lib/apt/lists/*
WORKDIR /srv/tg
COPY ./Build/LinuxServer/ /srv/tg/
COPY ./ServerConfig/server.yaml /srv/tg/server.yaml
EXPOSE 7777/udp 7778/udp 27015/udp
ENTRYPOINT ["/srv/tg/TerminalGroundsServer", "-log", "-unattended", "-Port=7777", "-QueryPort=27015", "-Config=/srv/tg/server.yaml"]
