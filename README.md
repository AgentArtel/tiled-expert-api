# Tiled AI Expert Agent

An AI-powered expert agent for the Tiled map editor, built using the `pydantic-ai` framework. This agent helps users with questions about Tiled's features, best practices, and technical implementation details.

## 🌟 Features

- 🤖 AI-powered responses about Tiled's features and capabilities
- 📚 Technical guidance on map creation and editing
- ✨ Best practices for project organization
- 🎮 Game engine integration assistance
- ⚡ Performance optimization tips
- 🌐 Interactive web UI using Streamlit

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
```

## 💻 Usage

### Web Interface (Recommended)
Run the Streamlit web interface:
```bash
streamlit run streamlit_app.py
```

Features:
- 💬 Interactive chat interface
- 📖 Documentation resources
- 🔍 Quick access to common topics
- 📝 Chat history management

### Command Line Interface
Run the agent in command line mode:
```bash
python tiled_ai_expert.py
```

## 📚 Documentation

The agent uses RAG (Retrieval Augmented Generation) to provide accurate answers based on Tiled's documentation. Topics covered include:

- 🗺️ Map creation and editing
- 🎨 Layer and tileset management
- 🎯 Object placement and properties
- 📤 Export formats and engine integration
- 🤖 Automation and scripting
- ⚡ Best practices and optimization

## 🔌 API Usage

### Endpoint

```
POST /api/v1/tiled/ask
```

### Authentication

The API uses Bearer token authentication. Include your API key in the Authorization header:

```
Authorization: Bearer your_api_key
```

### Request Format

```json
{
    "query": "How do I create a new tileset in Tiled?",
    "user_id": "user123",
    "conversation_id": "conv123"  // Optional
}
```

### Response Format

```json
{
    "success": true,
    "message": "Successfully processed query",
    "data": {
        "response": "To create a new tileset in Tiled..."
    }
}
```

### Error Response

```json
{
    "success": false,
    "message": "Error processing query: [error details]"
}
```

### Example Usage

Using curl:
```bash
curl -X POST "https://your-api-url/api/v1/tiled/ask" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "How do I create a new tileset in Tiled?",
         "user_id": "user123",
         "conversation_id": "conv123"
     }'
```

Using Python:
```python
import requests

url = "https://your-api-url/api/v1/tiled/ask"
headers = {
    "Authorization": "Bearer your_api_key",
    "Content-Type": "application/json"
}
data = {
    "query": "How do I create a new tileset in Tiled?",
    "user_id": "user123",
    "conversation_id": "conv123"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## 🛠️ Development

### Updating Documentation Database
To refresh the documentation database:
```bash
python crawl_tiled_docs.py
```

### Project Structure
```
tiled-agent/
├── streamlit_app.py      # Streamlit web interface
├── tiled_ai_expert.py    # Core AI agent logic
├── crawl_tiled_docs.py   # Documentation crawler
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## 🚂 Deployment

### Railway Deployment
1. Fork this repository
2. Create a new project in [Railway](https://railway.app)
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy!

### Local Deployment
For local development or testing:
```bash
streamlit run streamlit_app.py
```

## 🐳 Docker Deployment

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [pydantic-ai](https://github.com/jxnl/pydantic-ai)
- Powered by [OpenAI](https://openai.com)
- Uses [Supabase](https://supabase.io) for data storage
- UI built with [Streamlit](https://streamlit.io)
