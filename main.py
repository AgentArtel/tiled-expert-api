from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
from datetime import datetime
import logging

from tiled_ai_expert import tiled_ai_expert, TiledAIDeps

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Tiled AI Expert API",
    description="AI-powered expert agent for the Tiled map editor",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Log configuration on startup."""
    logger.info("Starting Tiled AI Expert API")
    logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"Port: {os.getenv('PORT', '8001')}")
    
    # Verify required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "API_BEARER_TOKEN"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# CORS configuration
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Railway
@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    try:
        # Test Supabase connection
        supabase.table("tiled_conversations").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Supabase setup
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials")
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    logger.error(f"Error initializing Supabase: {str(e)}")
    raise

# OpenAI setup
try:
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("Missing OpenAI API key")
    openai_client = AsyncOpenAI(api_key=openai_key)
except Exception as e:
    logger.error(f"Error initializing OpenAI: {str(e)}")
    raise

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
    
    if not expected_token:
        raise HTTPException(status_code=500, detail="API token not configured")
    
    if token != expected_token:
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
        logger.error(f"Error storing conversation: {str(e)}")
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
        logger.error(f"Error in tiled_ai_expert_endpoint: {str(e)}")
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
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return AgentResponse(
            success=False,
            message=f"Error retrieving conversation history: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
