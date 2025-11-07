# ocp-dog-frontend-api

Microservicio Flask que actúa como proxy hacia el backend de perros. Expone dos endpoints:

- `GET /healthz` → devuelve `{ "status": "ok" }`.
- `GET /dog` → consume el backend definido en `BACKEND_URL` (por defecto `http://ocp-dog-backend-api:5002/dog`) y reenvía el JSON recibido.

El servicio escucha en el puerto `5001`. Si necesitas apuntar a otro backend (por ejemplo, uno levantado en tu máquina), sobreescribe la variable de entorno `BACKEND_URL` antes de iniciar el servidor.

## Ejecución local

1. Colócate en `ocp-dog-frontend-api/`.
2. (Opcional, pero recomendado) Crea y activa un entorno virtual.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. Instala dependencias y arranca el servicio.

   ```bash
   python -m pip install -r requirements.txt
   python app.py
   ```

4. Asegúrate de que el backend esté disponible. Si usas el repositorio `ocp-dog-backend-api`, ejecútalo aparte (`python app.py` en ese proyecto) y deja corriendo ambos servicios.
5. Comprueba que el proxy responda en `http://localhost:5001` usando los comandos del apartado "Pruebas de la API".

## Docker

1. Construye la imagen.

   ```bash
   docker build -t ocp-dog-frontend-api .
   ```

2. Arranca un contenedor publicando el puerto `5001`.

   ```bash
   docker run --rm -p 5001:5001 \
     -e BACKEND_URL="http://<host-del-backend>:5002/dog" \
     ocp-dog-frontend-api
   ```

3. Si el backend vive en otro contenedor, asegúrate de que ambos compartan red (por ejemplo, usando `--network` o `docker compose`).

## Pruebas de la API

- **Curl o navegador**
  ```bash
  curl http://localhost:5001/healthz  # -> {"status":"ok"}
  curl http://localhost:5001/dog      # -> {"status":"success","image":"https://..."}
  ```
  El endpoint `/dog` devuelve exactamente el payload emitido por el backend. Si éste responde un error o no es accesible, el proxy contestará con `502` y un mensaje descriptivo.

- **Postman / Alog / clientes HTTP**
  1. Configura una petición `GET` a `http://<host>:5001/healthz` o `/dog`.
  2. No necesitas headers ni body especiales; sólo asegúrate de que el backend definido por `BACKEND_URL` es accesible.
  3. Envía la solicitud y revisa las respuestas JSON anteriores.

## CI/CD

El workflow `.github/workflows/docker-build.yml` se ejecuta en cada push o pull request hacia `main` y:

- Usa Buildx para construir la imagen desde este repo.
- Inicia sesión en Docker Hub con los secretos `DOCKER_USERNAME` y `DOCKERHUB_TOKEN`.
- Publica la imagen como `docker.io/<DOCKER_USERNAME>/ocp-dog-frontend-api:<github.run_number>`, lo que garantiza tags únicos por ejecución.

Antes de activar el workflow, define esos secretos en la configuración del repositorio.
