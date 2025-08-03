start backend:
uvicorn Main:app --reload

rebuild docker app:
docker build -t echoiq .

#psycopg error corrected freeze

test backend routes:
curl http://localhost:8000/api

post method
curl -X POST http://localhost:8000/api/scrape
curl -X POST https://echoiq.onrender.com/api

render database
psql "postgresql://vongaimusvaire:g4GR5kB6oP7SKh1aZcN2CIq6mbf1N0N2@dpg-d26ok28gjchc73e9dgsg-a.oregon-postgres.render.com/echo_db_h8cz"