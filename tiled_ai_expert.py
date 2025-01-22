from __future__ import annotations as _annotations

from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import asyncio
import httpx
import os

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
from supabase import Client
from typing import List

load_dotenv()

llm = os.getenv('LLM_MODEL', 'gpt-4-turbo-preview')
model = OpenAIModel(llm)

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class TiledAIDeps:
    supabase: Client
    openai_client: AsyncOpenAI

system_prompt = """
You are an expert at Tiled - a flexible map editor, specifically focused on providing technical guidance to other AI agents working on game development tasks. You have access to Tiled's official documentation through a RAG system that retrieves relevant documentation chunks based on user queries.

ROLE AND CONTEXT:
You are a specialized agent designed to assist other AI agents in implementing Tiled-related features in their game development projects. Your primary focus is providing accurate, technical, and implementation-focused responses that other agents can directly use in their work.

KNOWLEDGE BOUNDARIES:
1. Your knowledge is limited to:
   - Official Tiled documentation
   - Public APIs and interfaces
   - Common integration patterns
   - Conversation history from previous interactions
   
2. You should NOT provide information about:
   - Internal implementation details unless publicly documented
   - Unreleased features
   - Third-party tools unless officially supported

HANDLING CONVERSATION HISTORY:
1. When a conversation_id is provided:
   - Review previous interactions in the conversation
   - Build upon previous context and explanations
   - Reference earlier questions and answers when relevant
   - Avoid repeating information unless explicitly requested
   - Note any changes in project requirements or constraints

2. Use conversation history to:
   - Maintain context across multiple queries
   - Track version-specific advice given
   - Follow up on implementation suggestions
   - Address previous uncertainties or gaps
   - Ensure consistency in recommendations

3. When referencing previous interactions:
   - Cite specific previous questions or answers
   - Explain how new information relates to previous responses
   - Update or correct previous information if needed
   - Maintain documentation status labels across conversations

HANDLING UNCERTAINTY AND DOCUMENTATION:
1. When providing information, ALWAYS clearly label content as one of:
   [DOCUMENTED]: Information directly from official Tiled documentation
   [CONCEPTUAL]: Suggested approaches or examples not from documentation
   [UNCERTAIN]: Information that cannot be verified in documentation

2. For ALL code examples, start with one of:
   ```[DOCUMENTED CODE] - language
   // Direct implementation from Tiled documentation
   ```
   OR
   ```[CONCEPTUAL CODE] - language
   // Suggested implementation, not from official documentation
   ```

3. For ALL technical claims:
   - Prefix with [DOCUMENTED] if from official sources
   - Prefix with [CONCEPTUAL] if based on common practices
   - Include specific documentation reference when available

4. When information is not in documentation:
   - Start response with "[DOCUMENTATION GAP] This information is not available in the official documentation."
   - Clearly separate any suggested approaches with "[CONCEPTUAL SOLUTION]"
   
5. For version-specific features:
   - Start with "[VERSION X.Y.Z]" for documented features
   - Include "[VERSION UNCERTAIN]" if version info is unclear

6. Implementation Details:
   - Label all implementation examples as either [DOCUMENTED] or [CONCEPTUAL]
   - Explicitly state when internal details are not documented
   - Separate documented features from suggested implementations

WHEN RESPONDING TO QUERIES:
1. ALWAYS analyze the following aspects of the requesting agent's query:
   - Original user task they're working on
   - Project context and framework being used
   - Specific technical issue or question
   - Any code examples or configurations provided
   - Previous interactions in the conversation history

2. Structure your responses in this order:
   a) Brief acknowledgment of the context and relevant history
   b) Technical solution with implementation details
   c) Code examples and configurations
   d) Integration guidance specific to their framework
   e) Common pitfalls and troubleshooting tips
   f) Sources and references

3. ALWAYS include these technical details:
   - File formats and structures (TMX, JSON, etc.)
   - Property names and their expected values
   - Data types and structures
   - Configuration parameters
   - Command-line instructions if relevant

4. For code and configuration examples:
   - Provide complete, working examples
   - Consider any framework or context from conversation history
   - Maintain consistency with previous code examples
   - Update examples based on feedback or issues raised

5. When building upon previous responses:
   - Reference relevant parts of previous answers
   - Highlight any changes or updates to previous advice
   - Address any questions or concerns raised earlier
   - Maintain consistency in terminology and approach

RESPONSE QUALITY REQUIREMENTS:
- Technical Accuracy: All information must be precise and implementation-ready
- Completeness: Cover all aspects needed for successful implementation
- Framework Awareness: Tailor advice to the specific game framework being used
- Code Quality: Provide production-ready code examples following best practices
- Integration Focus: Emphasize practical integration steps and considerations

DOCUMENTATION AND SOURCES:
1. ALWAYS use the retrieved documentation as your primary source
2. For EVERY technical claim or instruction:
   - Cite the specific documentation section
   - Include the full URL in parentheses
   - Note any version-specific details

3. When documentation is insufficient:
   - Clearly state that you're providing a general solution
   - Base responses on established Tiled practices
   - Recommend consulting specific documentation sections

FORMAT YOUR RESPONSES:
1. Use clear hierarchical structure:
   # Main Topic
   ## Subtopic
   ### Implementation Details

2. Use code blocks with documentation status:
   ```[DOCUMENTED CODE] json
   {
     "example": "configuration"
   }
   ```
   OR
   ```[CONCEPTUAL CODE] json
   {
     "example": "suggested_configuration"
   }
   ```

3. Highlight important warnings:
   > ⚠️ Important: Critical information here

4. End with:
   ### Documentation Coverage
   - [DOCUMENTED]: List of features covered by official documentation
   - [CONCEPTUAL]: List of suggested implementations
   - [UNCERTAIN]: List of areas lacking documentation
   
   ### Sources
   - [Relevant URLs with descriptions]
   ### Related Topics
   - Suggested further reading

Remember: Your responses will be used by other AI agents to implement solutions, so focus on providing complete, accurate, and implementation-ready guidance with clear distinction between documented and conceptual content.
"""

async def get_embedding(text: str, openai_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error

@dataclass
class TiledAIDeps:
    supabase: Client
    openai_client: AsyncOpenAI

async def retrieve_relevant_documentation(ctx: RunContext[TiledAIDeps], user_query: str) -> str:
    """
    Retrieve relevant documentation chunks based on the query with RAG.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The user's question or query
        
    Returns:
        A formatted string containing the top most relevant documentation chunks
    """
    try:
        print(f"\nProcessing query: {user_query}")
        
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query, ctx.deps.openai_client)
        print("Generated query embedding")
        
        # Query Supabase for relevant documents
        print("Querying Supabase...")
        result = ctx.deps.supabase.rpc(
            'match_tiled_docs',
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                'filter': {}  # No filter to get all results
            }
        ).execute()
        
        print(f"Supabase query result: {result}")
        print(f"Number of matches found: {len(result.data) if result.data else 0}")
        
        if not result.data:
            print("No documentation found")
            return "I couldn't find any specific documentation that answers your question directly. I'll provide a general response based on my knowledge of Tiled, but please note that it may not be as detailed as documentation-based answers."
            
        # Format the results with sections and relevance scores
        formatted_chunks = []
        for doc in result.data:
            similarity = doc.get('similarity', 0)
            print(f"Document similarity: {similarity:.2%}")
            
            if similarity < 0.5:  # Lower threshold for more results
                print(f"Skipping document due to low similarity: {similarity:.2%}")
                continue
                
            chunk_text = f"""
### {doc['title']} (Relevance: {similarity:.2%})

{doc['content']}

📚 Source: {doc['url']}
⏰ Last Updated: {doc.get('updated_at', 'N/A')}
"""
            formatted_chunks.append((similarity, chunk_text))
            
        # Sort by relevance and join chunks
        formatted_chunks.sort(reverse=True, key=lambda x: x[0])
        chunks_text = "\n\n---\n\n".join(chunk[1] for chunk in formatted_chunks)
        
        if not formatted_chunks:
            print("No chunks passed similarity threshold")
            return "While I found some documentation, none of it was relevant enough to your specific question. I'll provide a general response based on my knowledge of Tiled."
            
        print(f"Returning {len(formatted_chunks)} relevant chunks")
        return f"I found {len(formatted_chunks)} relevant documentation sections that should help answer your question:\n\n{chunks_text}"
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in retrieve_relevant_documentation: {error_msg}")
        if "connection" in error_msg.lower():
            return "I'm having trouble connecting to the documentation database. I'll provide a general response based on my knowledge of Tiled."
        elif "embedding" in error_msg.lower():
            return "I'm having trouble processing your query. Could you please rephrase it?"
        else:
            return "I encountered an error while searching the documentation. I'll provide a general response based on my knowledge of Tiled."

async def list_documentation_pages(ctx: RunContext[TiledAIDeps]) -> List[str]:
    """
    Retrieve a list of all available Tiled documentation pages.
    
    Returns:
        List[str]: List of unique URLs for all documentation pages
    """
    try:
        # Query Supabase for unique URLs where source is tiled_docs
        result = ctx.deps.supabase.from_('tiled_docs_pages') \
            .select('url') \
            .eq('metadata->>source', 'tiled_docs') \
            .execute()
        
        if not result.data:
            return []
            
        # Extract unique URLs
        urls = sorted(set(doc['url'] for doc in result.data))
        return urls
        
    except Exception as e:
        print(f"Error retrieving documentation pages: {e}")
        return []

async def get_page_content(ctx: RunContext[TiledAIDeps], url: str) -> str:
    """
    Retrieve the full content of a specific documentation page by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        url: The URL of the page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        result = ctx.deps.supabase.from_('tiled_docs_pages') \
            .select('title, content, chunk_number') \
            .eq('url', url) \
            .eq('metadata->>source', 'tiled_docs') \
            .order('chunk_number') \
            .execute()
        
        if not result.data:
            return f"No content found for URL: {url}"
            
        # Format the page with its title and all chunks
        page_title = result.data[0]['title'].split(' - ')[0]  # Get the main title
        formatted_content = [f"# {page_title}\n"]
        
        # Add each chunk's content
        for chunk in result.data:
            formatted_content.append(chunk['content'])
            
        # Join everything together
        return "\n\n".join(formatted_content)
        
    except Exception as e:
        print(f"Error retrieving page content: {e}")
        return f"Error retrieving page content: {str(e)}"

async def check_database_content(ctx: RunContext[TiledAIDeps]) -> str:
    """
    Check the content of the Supabase database.
    """
    try:
        # Query for all records
        result = ctx.deps.supabase.table('tiled_docs_pages').select('*').execute()
        
        if not result.data:
            return "No records found in the database."
            
        # Get some basic stats
        total_records = len(result.data)
        unique_urls = len(set(doc['url'] for doc in result.data))
        
        # Sample a few records
        sample_size = min(3, total_records)
        sample_records = result.data[:sample_size]
        
        sample_info = []
        for doc in sample_records:
            sample_info.append(f"""
Title: {doc['title']}
URL: {doc['url']}
Chunk Number: {doc['chunk_number']}
Has Embedding: {'Yes' if doc['embedding'] else 'No'}
""")
            
        return f"""Database Content Summary:
Total Records: {total_records}
Unique URLs: {unique_urls}

Sample Records:
{'---'.join(sample_info)}
"""
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error checking database: {error_msg}")
        return f"Error checking database: {error_msg}"

async def main():
    from supabase import create_client
    
    # Initialize clients
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    deps = TiledAIDeps(supabase=supabase, openai_client=openai_client)
    
    # Technical integration and scalability focused questions
    test_questions = [
        "How do I integrate Tiled maps with Unity, including handling tile animations and custom properties? What are the performance considerations for large maps?",
        "What's the best way to handle version control for a Tiled project with multiple team members? Include handling of binary files and conflict resolution.",
        "How can I create custom exporters for Tiled maps? Show an example of exporting to a custom JSON format with specific game engine requirements.",
        "What are the performance implications of using animated tiles and how can I optimize them for mobile games? Include memory usage considerations.",
        "How do I set up a continuous integration pipeline for Tiled maps, including automated validation and testing of map properties?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print("\n" + "="*80)
        print(f"Technical Test {i}/5: {question}")
        print("="*80 + "\n")
        print("Expected Coverage:")
        print("- Technical Implementation")
        print("- Performance Considerations")
        print("- Integration Details")
        print("- Scalability Aspects")
        print("- Common Pitfalls\n")
        
        result = await tiled_ai_expert.run(question, deps=deps)
        print("\nAnswer:")
        print(result.data)
        print("\nEvaluation:")
        print("- Technical Depth: Is the explanation detailed and implementation-focused?")
        print("- Performance Analysis: Are optimization strategies discussed?")
        print("- Integration Guide: Are steps clear and complete?")
        print("- Scalability Coverage: Are large-scale considerations addressed?")
        print("- Error Handling: Are common issues and solutions covered?")
        print("\n")

# Initialize the agent with tools
tiled_ai_expert = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=TiledAIDeps,
    retries=2
)

if __name__ == "__main__":
    asyncio.run(main())
