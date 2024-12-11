from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.routers import llm_rag_chat

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

origins = ["http://35.185.56.27", "http://34.23.190.158.sslip.io"]
# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to PourfectAI - where every pour is perfectly yours!"}

@app.get("/status")
async def get_api_status():
    return {
        "version": "3.1",
    }

# Additional routers here
app.include_router(llm_rag_chat.router, prefix="/llm-rag")