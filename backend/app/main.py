from fastapi import FastAPI

app = FastAPI(title="AI Library Management System")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}