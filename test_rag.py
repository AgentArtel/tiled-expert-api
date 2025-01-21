import json
import time
from datetime import datetime
import os
import openai
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_SERVICE_KEY", "")
)

# Test queries organized by categories
test_queries = {
    "Basic Understanding": [
        "What are the main features of Tiled?",
        "Explain what a tileset is in Tiled",
        "What's the difference between tile layers and object layers?"
    ],
    "Technical/Format": [
        "What's the structure of a TMX file?",
        "How do I export maps to JSON format?",
        "What compression methods are supported for tile layer data?"
    ],
    "How-to/Workflow": [
        "How do I create an animated tile?",
        "What's the process for creating a collision layer?",
        "How can I import external tilesets?"
    ],
    "Advanced Features": [
        "How do custom properties work in Tiled?",
        "Explain how to use terrain brushes",
        "What are template objects and how do I use them?"
    ],
    "Troubleshooting": [
        "What should I do if my tileset images aren't loading?",
        "How do I fix broken tileset references?",
        "Common issues when exporting maps"
    ],
    "Integration": [
        "Which game engines support Tiled maps?",
        "How can I integrate Tiled maps with Unity?",
        "What's the best way to load Tiled maps in Python?"
    ],
    "Complex Scenarios": [
        "Walk me through creating a multi-layered map with both tiles and objects",
        "How do I set up an isometric map with custom properties and collision?",
        "Explain the workflow for creating a map with animated water tiles and collision areas"
    ],
    "Version-Specific": [
        "What are the new features in the latest version?",
        "Are there any breaking changes in recent updates?",
        "How has the TMX format evolved?"
    ]
}

def match_documents(query: str, match_count: int = 5) -> list:
    """Search for relevant documents using the match_tiled_docs function."""
    response = supabase.rpc(
        'match_tiled_docs',
        {
            'query_embedding': get_embedding(query),
            'match_count': match_count
        }
    ).execute()
    
    return response.data

def get_embedding(text: str) -> list:
    """Get embedding for a text using OpenAI's API."""
    try:
        client = openai.OpenAI()
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        return []

def get_completion(messages: list) -> str:
    """Get completion from OpenAI's API."""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4"),
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting completion: {str(e)}")
        return ""

def test_query(query: str) -> dict:
    """Test a single query and return the results."""
    print(f"\nTesting query: {query}")
    
    start_time = time.time()
    
    # Get relevant documents
    matches = match_documents(query)
    
    # Prepare context from matches
    context = "\n\n".join([
        f"Source: {match['url']}\nContent: {match['content']}"
        for match in matches
    ])
    
    # Prepare messages for the LLM
    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions about the Tiled map editor based on the provided documentation. Always cite your sources using the provided URLs."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nPlease provide a detailed answer based on the context above. Include relevant source URLs in your response."}
    ]
    
    # Get response from LLM
    response = get_completion(messages)
    
    end_time = time.time()
    
    return {
        "query": query,
        "response": response,
        "matches": matches,
        "execution_time": end_time - start_time
    }

def run_tests():
    """Run all test queries and save results."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "categories": {}
    }
    
    for category, queries in test_queries.items():
        print(f"\nTesting category: {category}")
        category_results = []
        
        for query in queries:
            try:
                result = test_query(query)
                category_results.append(result)
            except Exception as e:
                print(f"Error testing query '{query}': {str(e)}")
                category_results.append({
                    "query": query,
                    "error": str(e)
                })
        
        results["categories"][category] = category_results
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_test_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {filename}")
    return results

if __name__ == "__main__":
    run_tests()
