# Tiled AI Expert Agent

An AI-powered expert agent for the Tiled map editor, built using the `pydantic-ai` framework. This agent provides detailed, documented-based guidance about Tiled's features, best practices, and technical implementation details, with clear distinction between documented features and conceptual solutions.

## 🌟 Features

- 🤖 AI-powered responses with clear distinction between documented and conceptual content
- 📚 RAG-enhanced responses using official Tiled documentation
- ✨ Version-specific feature information and compatibility notes
- 🎮 Game engine integration guidance with implementation examples
- ⚡ Performance optimization recommendations
- 🌐 Interactive web UI using Streamlit

## 🎯 Response Quality

The agent provides responses with:
- Clear distinction between documented features and conceptual solutions
- Version-specific information and compatibility notes
- Implementation examples marked as either documented or conceptual
- Explicit acknowledgment of documentation gaps
- Comprehensive source references and related topics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/tiled-agent.git
cd tiled-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables by copying `.env.example` to `.env`:
```bash
cp .env.example .env
```
Then edit `.env` with your credentials:
```
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
LLM_MODEL=gpt-4-turbo-preview

# Supabase Configuration (for conversation history)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_key

# API Configuration
API_BEARER_TOKEN=your_api_key
PORT=8001

# Tiled Documentation Crawler Settings
TILED_BASE_URL=https://doc.mapeditor.org/en/stable/
MAX_CONCURRENT_REQUESTS=5
CHUNK_SIZE=4000
FOLLOW_LINKS=true
MAX_DEPTH=3
```

## 💻 Usage

### Web Interface (Recommended)
Run the Streamlit web interface:
```bash
streamlit run streamlit_app.py
```

Features:
- 💬 Interactive chat interface with documentation-aware responses
- 📖 Access to official Tiled documentation
- 🔍 Clear distinction between documented and conceptual solutions
- 📝 Version-specific information and compatibility notes

### API Usage

The API provides detailed responses with clear distinction between documented features and conceptual solutions, along with conversation history tracking.

#### Endpoints

1. **Ask Questions**
```
POST /api/v1/tiled/ask
```

2. **Get Conversation History**
```
GET /api/v1/tiled/conversations/{conversation_id}
```

#### Authentication
```
Authorization: Bearer your_api_key
```

#### Example Usage

1. **Start a New Conversation**
```bash
# Generate a conversation ID
CONV_ID="conv_$(uuidgen)"

# Make your first query
curl -X POST "http://localhost:8001/api/v1/tiled/ask" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "What is Tiled?",
         "user_id": "user123",
         "conversation_id": "'$CONV_ID'"
     }'
```

2. **Continue the Conversation**
```bash
# Make subsequent queries with the same conversation ID
curl -X POST "http://localhost:8001/api/v1/tiled/ask" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "How do I create a new map?",
         "user_id": "user123",
         "conversation_id": "'$CONV_ID'"
     }'
```

3. **View Conversation History**
```bash
curl "http://localhost:8001/api/v1/tiled/conversations/$CONV_ID" \
     -H "Authorization: Bearer your_api_key"
```

#### Response Format

1. **Ask Endpoint Response**
```json
{
    "success": true,
    "message": "Successfully processed query",
    "data": {
        "response": "# Main Topic\n\n[DOCUMENTED] Official feature information...\n\n[CONCEPTUAL] Suggested implementation...\n\n### Documentation Coverage\n- [DOCUMENTED]: List of documented features\n- [CONCEPTUAL]: List of suggested implementations\n- [UNCERTAIN]: Areas lacking documentation"
    }
}
```

2. **Conversation History Response**
```json
{
    "success": true,
    "message": "Successfully retrieved conversation history",
    "data": {
        "history": [
            {
                "id": "uuid",
                "user_id": "user123",
                "conversation_id": "conv_xxx",
                "query": "What is Tiled?",
                "response": "...",
                "metadata": {
                    "source": "tiled_ai_expert",
                    "documentation_coverage": {
                        "documented": "Official features and APIs",
                        "conceptual": "Implementation suggestions",
                        "uncertain": "Undocumented features"
                    },
                    "sources": [
                        "Tiled Documentation - Getting Started",
                        "Tiled Documentation - Manual"
                    ],
                    "interaction_type": "query_response"
                },
                "created_at": "2025-01-21T00:00:00Z",
                "updated_at": "2025-01-21T00:00:00Z"
            }
        ]
    }
}
```

#### Database Schema
The conversation history is stored in a Supabase database with the following schema:
```sql
create table tiled_conversations (
    id uuid default uuid_generate_v4() primary key,
    user_id text not null,
    conversation_id text not null,
    query text not null,
    response text not null,
    metadata jsonb default '{}'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Features of Conversation History
- 🔄 Persistent conversation tracking
- 📝 Complete query and response history
- 🕒 Timestamps for all interactions
- 📊 Rich metadata storage:
  - 🎯 Source of response (e.g., tiled_ai_expert)
  - 📚 Documentation coverage analysis
  - 📖 Referenced documentation sources
  - 🔍 Interaction type classification
- 🏷️ Extensible metadata structure for analytics
- 🔍 Fast retrieval by conversation ID

### Metadata Structure
The metadata field captures rich information about each interaction:

1. **Source** (`source`): Identifies the AI model or component that generated the response
2. **Documentation Coverage** (`documentation_coverage`):
   - `documented`: Features with official documentation
   - `conceptual`: Implementation suggestions and best practices
   - `uncertain`: Areas with limited or no documentation
3. **Sources** (`sources`): List of documentation pages referenced
4. **Interaction Type** (`interaction_type`): Classification of the interaction (e.g., query_response)

This metadata enables:
- 📈 Response quality analysis
- 📊 Documentation coverage tracking
- 🎯 Source attribution
- 🔍 Enhanced search and filtering
- 📱 Integration with analytics tools

## 🛠️ Development

### Project Structure
```
tiled-agent/
├── streamlit_app.py           # Streamlit web interface
├── tiled_ai_expert.py         # Core AI agent with enhanced prompt
├── tiled_ai_expert_endpoint.py # FastAPI endpoint with conversation history
├── crawl_tiled_docs.py        # Documentation crawler
├── test_rag.py               # RAG system tests
├── tiled_conversations.sql    # Database schema for conversation history
├── requirements.txt          # Python dependencies
└── .env.example             # Example environment variables
```

### Recent Updates
- Added conversation history tracking with Supabase integration
- Enhanced system prompt for clearer documentation vs. conceptual content distinction
- Improved version-specific information handling
- Added explicit documentation coverage sections
- Enhanced code example labeling ([DOCUMENTED] vs [CONCEPTUAL])
- Improved uncertainty handling in responses

## 🚂 Deployment

### Railway Deployment
1. Fork this repository
2. Create a new project in [Railway](https://railway.app)
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy!

### Docker Deployment
1. Build the Docker image:
```bash
docker build -t tiled-ai-expert .
```

2. Run the container:
```bash
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=your_key \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_SERVICE_KEY=your_key \
  -e API_KEY=your_api_key \
  tiled-ai-expert
```

## 📚 Documentation

The agent uses RAG (Retrieval Augmented Generation) to provide accurate answers based on Tiled's documentation. Topics covered include:

- 🗺️ Map creation and editing
- 🎨 Layer and tileset management
- 🎯 Object placement and properties
- 📤 Export formats and engine integration
- 🤖 Automation and scripting
- ⚡ Best practices and optimization

## 🙏 Acknowledgments

- Built with [pydantic-ai](https://github.com/jxnl/pydantic-ai)
- Powered by [OpenAI](https://openai.com)
- Uses [Supabase](https://supabase.io) for data storage
- Documentation from [Tiled Map Editor](https://www.mapeditor.org/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
