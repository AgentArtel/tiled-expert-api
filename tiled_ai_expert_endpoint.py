from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

from tiled_ai_expert import tiled_ai_expert, TiledAIDeps

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# OpenAI setup
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request/Response Models
class AgentRequest(BaseModel):
    query: str
    user_id: str
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the bearer token against environment variable."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authorization credentials")
    
    token = credentials.credentials
    expected_token = os.getenv("API_BEARER_TOKEN")
    
    if not expected_token or token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return True

async def store_conversation(
    user_id: str,
    conversation_id: str,
    query: str,
    response: str,
    metadata: Optional[Dict] = None
):
    """Store conversation in Supabase."""
    try:
        # Extract documentation coverage from response
        coverage = {}
        for line in response.split('\n'):
            if line.strip().startswith('[DOCUMENTED]:'):
                coverage['documented'] = line.replace('[DOCUMENTED]:', '').strip()
            elif line.strip().startswith('[CONCEPTUAL]:'):
                coverage['conceptual'] = line.replace('[CONCEPTUAL]:', '').strip()
            elif line.strip().startswith('[UNCERTAIN]:'):
                coverage['uncertain'] = line.replace('[UNCERTAIN]:', '').strip()

        # Extract sources from response
        sources = []
        in_sources = False
        for line in response.split('\n'):
            if line.strip() == '### Sources':
                in_sources = True
            elif in_sources and line.strip().startswith('### '):
                in_sources = False
            elif in_sources and line.strip().startswith('- '):
                sources.append(line.strip()[2:])

        # Create metadata
        metadata = metadata or {}
        metadata.update({
            'source': 'tiled_ai_expert',
            'documentation_coverage': coverage,
            'sources': sources,
            'interaction_type': 'query_response'
        })
        
        data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query": query,
            "response": response,
            "metadata": metadata
        }
        
        result = supabase.table("tiled_conversations").insert(data).execute()
        return result
    except Exception as e:
        print(f"Error storing conversation: {str(e)}")
        return None

@app.post("/api/v1/tiled/ask", response_model=AgentResponse)
async def tiled_ai_expert_endpoint(
    request: AgentRequest,
    authenticated: bool = Depends(verify_token)
):
    """
    Endpoint for querying the Tiled AI expert.
    
    Args:
        request: AgentRequest containing query and user information
        authenticated: Boolean indicating if request is authenticated
        
    Returns:
        AgentResponse containing success status and response data
    """
    try:
        # Initialize dependencies
        deps = TiledAIDeps(
            supabase=supabase,
            openai_client=openai_client
        )
        
        # Get response from Tiled AI expert
        result = await tiled_ai_expert.run(
            request.query,
            deps=deps
        )
        
        # Store conversation if conversation_id provided
        if request.conversation_id:
            await store_conversation(
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                query=request.query,
                response=result.data
            )
        
        return AgentResponse(
            success=True,
            message="Successfully processed query",
            data={"response": result.data}
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Error processing query: {str(e)}"
        )

@app.get("/api/v1/tiled/conversations/{conversation_id}", response_model=AgentResponse)
async def get_conversation_history(
    conversation_id: str,
    authenticated: bool = Depends(verify_token)
):
    """
    Get conversation history for a specific conversation ID.
    """
    try:
        result = supabase.table("tiled_conversations").select("*").eq("conversation_id", conversation_id).execute()
        
        if not result.data:
            return AgentResponse(
                success=False,
                message=f"No conversation found with ID: {conversation_id}"
            )
            
        return AgentResponse(
            success=True,
            message="Successfully retrieved conversation history",
            data={"history": result.data}
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Error retrieving conversation history: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
