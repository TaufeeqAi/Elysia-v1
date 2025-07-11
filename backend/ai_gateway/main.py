from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ai_factory.factory import create_llm, create_chat_chain
import asyncio

app = FastAPI(title="AI Gateway")

class ChatRequest(BaseModel):
    provider: str
    api_key: str
    prompt: str
    model: str | None = None

async def stream_response(chain, user_input: str):
    """Stream LLM response token-by-token."""
    async for token in chain.astream({"input": user_input}):
        yield token

@app.post("/ai/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize LLM and chain
        llm = create_llm(request.provider, request.api_key, request.model)
        chain = create_chat_chain(llm)

        # Return streaming response
        return StreamingResponse(
            stream_response(chain, request.prompt),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}