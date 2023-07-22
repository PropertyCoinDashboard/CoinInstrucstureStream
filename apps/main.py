from fastapi import FastAPI

app = FastAPI()


@app.get("/coin")
def hello_api():
    return "Hello"
