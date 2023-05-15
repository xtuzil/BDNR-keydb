# BDNR-keydb

To run fastapi server with keydb (docker needs to be installed):

```
cd server
docker compose build && docker compose up
```

To run angular client (npm needs to be installed):

```
cd client/chat
npm install
ng serve
```

To insert init data (with users) send POST request to http://localhost:8000/init

```
curl -X POST http://localhost:8000/init
```

There is also REST API (Swagger) documentation available at http://localhost:8000/docs
