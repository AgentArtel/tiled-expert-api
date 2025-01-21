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
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_key
LLM_MODEL=gpt-4-turbo-preview
API_KEY=your_api_key
PORT=8001
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

The API provides detailed responses with clear distinction between documented features and conceptual solutions.

#### Endpoint
```
POST /api/v1/tiled/ask
```

#### Authentication
```
Authorization: Bearer your_api_key
```

#### Example Queries and Responses

1. **Basic Feature Query**
```bash
curl -X POST "http://localhost:8001/api/v1/tiled/ask" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "What is the latest version of Tiled and what are the system requirements?",
         "user_id": "user123"
     }'
```

2. **Technical Implementation Query**
```bash
curl -X POST "http://localhost:8001/api/v1/tiled/ask" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "How can I implement a system for dynamic terrain modification in Tiled that affects the appearance of tiles during gameplay?",
         "user_id": "user123"
     }'
```

3. **Integration Query**
```bash
curl -X POST "http://localhost:8001/api/v1/tiled/ask" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "How should I structure my Tiled project for a large RPG game with multiple maps and shared tilesets?",
         "user_id": "user123"
     }'
```

#### Response Format
Responses are structured with clear sections:
```json
{
    "success": true,
    "message": "Successfully processed query",
    "data": {
        "response": "# Main Topic\n\n[DOCUMENTED] Official feature information...\n\n[CONCEPTUAL] Suggested implementation...\n\n### Documentation Coverage\n- [DOCUMENTED]: List of documented features\n- [CONCEPTUAL]: List of suggested implementations\n- [UNCERTAIN]: Areas lacking documentation"
    }
}
```

## 🛠️ Development

### Project Structure
```
tiled-agent/
├── streamlit_app.py           # Streamlit web interface
├── tiled_ai_expert.py         # Core AI agent with enhanced prompt
├── tiled_ai_expert_endpoint.py # FastAPI endpoint
├── crawl_tiled_docs.py        # Documentation crawler
├── test_rag.py               # RAG system tests
├── requirements.txt          # Python dependencies
└── .env.example             # Example environment variables
```

### Recent Updates
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
