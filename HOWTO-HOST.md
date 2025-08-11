# HOWTO-HOST

1) Build LinuxServer binary via UE (see HOWTO-BUILD.md). Copy output into Build/LinuxServer/.
2) Configure `ServerConfig/server.yaml` as needed.
3) Build and run Docker:
   - docker build -t terminalgrounds/server:dev Docker
   - docker compose up -d

Ports: 7777/udp (game), 27015/udp (query). Edit docker-compose.yml to map as needed.
 