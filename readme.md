start backend:
uvicorn Main:app --reload

rebuild docker app:
docker build -t echoiq .

#edit

test backend routes:
curl http://localhost:8000/api