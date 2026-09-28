from fastapi import FastAPI

app = FastAPI(
    title="AI Cloud Cost Detective",
    description="AI-powered AWS cloud cost analysis and optimization platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-cloud-cost-detective",
        "version": "0.1.0",
    }


@app.get("/")
def root():
    return {
        "message": "AI Cloud Cost Detective API"
    }