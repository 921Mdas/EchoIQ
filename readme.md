start backend:
uvicorn Main:app --reload

rebuild docker app:
docker build -t echoiq .

#psycopg error corrected freeze

test backend routes:
docker build -t echoiq .
docker compose down -v && docker compose up --build
docker-compose logs db
docker ps
docker logs echoiq-app-1
normal user: docker exec -it echoiq-db-1 psql -U vongaimusvaire -d echo_db
super user: docker exec -it echoiq-db-1 psql -U postgres -d echo_db

who are you connected as?
\conninfo


docker system prune -a --volumes

docker run -p 8000:8000 -e DATABASE_URL="postgresql://vongaimusvaire:MySushi32@db:5432/echo_db" echoiq-app:latest


post method
curl -X POST http://localhost:8000/api/scrape
curl -X POST https://echoiq.onrender.com/api
docker curl -X POST http://0.0.0.0:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "rodeomads@gmail.com", "password": "00921"}'

render database
psql "postgresql://vongaimusvaire:g4GR5kB6oP7SKh1aZcN2CIq6mbf1N0N2@dpg-d26ok28gjchc73e9dgsg-a.oregon-postgres.render.com/echo_db_h8cz"

pip freeze 
pip freeze > requirements.txt

source venv/bin/activate
