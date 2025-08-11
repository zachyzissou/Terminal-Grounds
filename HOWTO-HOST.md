# HOWTO-HOST

1) Build LinuxServer binary via UE (see HOWTO-BUILD.md). Copy output into Build/LinuxServer/.
2) Configure `ServerConfig/server.yaml` as needed.
3) Build and run Docker:
   - docker build -t terminalgrounds/server:dev Docker
   - docker compose up -d

Ports: 7777/udp (game), 27015/udp (query). Edit docker-compose.yml to map as needed.

## Tips

- Persist saves/configs by mounting volumes to `/srv/tg/Saved/` and mapping `server.yaml` as needed.
- Use environment variables via `docker-compose.yml` to pass session name, max players, etc., if desired.
 
### Example docker-compose.yml

services:
   tg-server:
      image: terminalgrounds/server:dev
      ports:
         - "7777:7777/udp"
         - "27015:27015/udp"
      volumes:
         - ./ServerConfig/server.yaml:/srv/tg/server.yaml:ro
         - ./Saved/:/srv/tg/Saved/
      environment:
         - TG_SESSION=Playtest
         - TG_MAXPLAYERS=8
 