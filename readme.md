start backend:
uvicorn Main:app --reload

rebuild docker app:
docker build -t echoiq .

#psycopg error corrected freeze

test backend routes:
curl http://localhost:8000/api