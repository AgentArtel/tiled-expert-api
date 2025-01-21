import os
import sys
import json
import asyncio
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
from xml.etree import ElementTree

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from openai import AsyncOpenAI
from supabase import create_client, Client

load_dotenv()

# Initialize OpenAI and Supabase clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]

def chunk_text(text: str, chunk_size: int = 4000) -> List[str]:
    """Split text into chunks, respecting Tiled documentation structure."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find section breaks first (## or #)
        chunk = text[start:end]
        section_break = max(
            chunk.rfind('\n## '),
            chunk.rfind('\n# ')
        )
        if section_break != -1 and section_break > chunk_size * 0.3:
            end = start + section_break

        # Try to find code block boundary
        elif '```' in chunk:
            code_block = chunk.rfind('```')
            if code_block != -1 and code_block > chunk_size * 0.3:
                end = start + code_block

        # Try paragraph breaks
        elif '\n\n' in chunk:
            last_break = chunk.rfind('\n\n')
            if last_break > chunk_size * 0.3:
                end = start + last_break

        # Last resort: break at sentence
        elif '. ' in chunk:
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.3:
                end = start + last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end

    return chunks

async def get_title_and_summary(chunk: str, url: str) -> Dict[str, str]:
    """Extract title and summary using GPT-4, optimized for Tiled documentation."""
    system_prompt = """You are an AI that extracts titles and summaries from Tiled documentation chunks.
    For the given documentation chunk, extract or generate:
    1. A clear, descriptive title that reflects the main topic
    2. A concise summary of the key points
    3. Additional metadata about the content

    Format your response as a JSON object with these exact keys:
    {
        "title": "The main topic or section title",
        "summary": "A clear summary of the main points",
        "metadata": {
            "category": "Documentation category (e.g. Manual, Reference)",
            "features": ["List of Tiled features mentioned"],
            "file_formats": ["Any file formats discussed"],
            "version_info": "Any version-specific information"
        }
    }"""
    
    try:
        # Add delay to avoid rate limits
        await asyncio.sleep(1)
        
        response = await openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{chunk}"}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate response format
        required_keys = ["title", "summary", "metadata"]
        if not all(key in result for key in required_keys):
            raise ValueError("Missing required keys in API response")
            
        return result
    except Exception as e:
        print(f"Error getting title and summary for {url}: {str(e)}")
        return {
            "title": f"Processing Error: {url.split('/')[-2]}",
            "summary": f"Failed to process content: {str(e)}",
            "metadata": {
                "category": "Error",
                "features": [],
                "file_formats": [],
                "version_info": None,
                "error": str(e)
            }
        }

async def get_embedding(text: str) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

async def process_chunk(chunk: str, chunk_number: int, url: str) -> ProcessedChunk:
    """Process a single chunk of text."""
    # Get title, summary, and metadata
    result = await get_title_and_summary(chunk, url)
    
    # Get embedding
    embedding = await get_embedding(chunk)
    
    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=result.get("title", ""),
        summary=result.get("summary", ""),
        content=chunk,
        metadata=result.get("metadata", {}),
        embedding=embedding
    )

async def insert_chunk(chunk: ProcessedChunk):
    """Insert a processed chunk into Supabase."""
    try:
        data = {
            "url": chunk.url,
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding
        }
        
        response = supabase.table("tiled_docs_pages").insert(data).execute()
        print(f"Inserted chunk {chunk.chunk_number} from {chunk.url}")
        return response
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None

async def process_and_store_document(url: str, markdown: str):
    """Process a document and store its chunks."""
    print(f"Processing document: {url}")
    
    try:
        # Process chunks
        chunks = chunk_text(markdown)
        for i, chunk in enumerate(chunks):
            processed_chunk = await process_chunk(chunk, i, url)
            if processed_chunk:
                await insert_chunk(processed_chunk)
                await asyncio.sleep(0.5)  # Rate limiting between chunks
        
        print(f"Completed processing document: {url}")
        
    except Exception as e:
        print(f"Error processing document {url}: {e}")

async def get_tiled_docs_urls() -> List[str]:
    """Get URLs from Tiled documentation structure."""
    base_url = "https://doc.mapeditor.org/en/stable/"
    
    # Define all documentation sections and subsections
    sections = [
        # User Manual
        "manual/introduction/",
        "manual/about/",
        "manual/getting-started/",
        "manual/projects/",
        "manual/projects-whats-in/",
        "manual/sessions/",
        "manual/opening-file-in-project/",
        "manual/layers/",
        "manual/layers/layer-types/",
        "manual/layers/parallax/",
        "manual/layers/tinting/",
        "manual/editing-tile-layers/",
        "manual/editing-tile-layers/stamp/",
        "manual/editing-tile-layers/terrain/",
        "manual/editing-tile-layers/bucket-fill/",
        "manual/editing-tile-layers/shape-fill/",
        "manual/editing-tile-layers/eraser/",
        "manual/editing-tile-layers/selection/",
        "manual/editing-tile-layers/tile-stamps/",
        "manual/objects/",
        "manual/objects/placement/",
        "manual/objects/select/",
        "manual/objects/edit-polygons/",
        "manual/objects/connecting/",
        "manual/editing-tilesets/",
        "manual/editing-tilesets/tileset-types/",
        "manual/editing-tilesets/tileset-properties/",
        "manual/editing-tilesets/tile-properties/",
        "manual/editing-tilesets/terrain/",
        "manual/editing-tilesets/tile-collision-editor/",
        "manual/editing-tilesets/tile-animation-editor/",
        "manual/custom-properties/",
        "manual/custom-properties/adding/",
        "manual/custom-properties/custom-types/",
        "manual/custom-properties/tile-property-inheritance/",
        "manual/using-templates/",
        "manual/using-templates/creating-templates/",
        "manual/using-templates/creating-instances/",
        "manual/using-templates/editing-templates/",
        "manual/using-templates/detaching/",
        "manual/terrain/",
        "manual/terrain/define/",
        "manual/terrain/editing/",
        "manual/terrain/fill-mode/",
        "manual/terrain/probability/",
        "manual/terrain/transformations/",
        "manual/terrain/final-words/",
        "manual/using-infinite-maps/",
        "manual/using-infinite-maps/creating/",
        "manual/using-infinite-maps/editing/",
        "manual/using-infinite-maps/converting/",
        "manual/worlds/",
        "manual/worlds/defining/",
        "manual/worlds/editing/",
        "manual/worlds/pattern-matching/",
        "manual/worlds/direct-neighbors/",
        "manual/using-commands/",
        "manual/using-commands/command-button/",
        "manual/using-commands/editing/",
        "manual/using-commands/examples/",
        "manual/automapping/",
        "manual/automapping/introduction/",
        "manual/automapping/rules-file/",
        "manual/automapping/rule-map/",
        "manual/automapping/properties/",
        "manual/automapping/examples/",
        "manual/automapping/legacy/",
        "manual/automapping/credits/",
        "manual/export/",
        "manual/export/generic/",
        "manual/export/defold/",
        "manual/export/gmx/",
        "manual/export/yy/",
        "manual/export/godot/",
        "manual/export/tbin/",
        "manual/export/other/",
        "manual/export/custom/",
        "manual/export/python/",
        "manual/export/image/",
        "manual/keyboard-shortcuts/",
        "manual/preferences/",
        "manual/preferences/general/",
        "manual/preferences/interface/",
        "manual/preferences/keyboard/",
        "manual/preferences/theme/",
        "manual/preferences/plugins/",
        "manual/scripting/",
        "manual/scripting/introduction/",
        "manual/scripting/reference/",
        
        # Reference Manual
        "reference/support-for-tmx-maps/",
        "reference/support-for-tmx-maps/libraries/",
        "reference/support-for-tmx-maps/languages/",
        "reference/support-for-tmx-maps/frameworks/",
        "reference/tmx-map-format/",
        "reference/tmx-map-format/map/",
        "reference/tmx-map-format/editorsettings/",
        "reference/tmx-map-format/tileset/",
        "reference/tmx-map-format/layer/",
        "reference/tmx-map-format/objectgroup/",
        "reference/tmx-map-format/imagelayer/",
        "reference/tmx-map-format/group/",
        "reference/tmx-map-format/properties/",
        "reference/tmx-map-format/template/",
        "reference/json-map-format/",
        "reference/json-map-format/map/",
        "reference/json-map-format/layer/",
        "reference/json-map-format/chunk/",
        "reference/json-map-format/object/",
        "reference/json-map-format/text/",
        "reference/json-map-format/tileset/",
        "reference/json-map-format/template/",
        "reference/json-map-format/property/",
        "reference/json-map-format/point/",
        "reference/tmx-changelog/",
        "reference/global-tile-ids/",
        "reference/global-tile-ids/flipping/",
        "reference/global-tile-ids/mapping/",
        "reference/global-tile-ids/example/"
    ]
    
    # Build full URLs
    urls = [urljoin(base_url, section) for section in sections]
    print(f"Found {len(urls)} documentation sections")
    return urls

async def crawl_parallel(urls: List[str], max_concurrent: int = 5):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    print("\n=== Parallel Crawling with Browser Reuse ===")
    
    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    
    # Configure crawler
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    # Create crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()
    
    try:
        success_count = 0
        fail_count = 0
        
        # Process URLs in batches
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i:i + max_concurrent]
            tasks = []
            
            for j, url in enumerate(batch):
                session_id = f"session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)
            
            # Wait for batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    print(f"Successfully crawled: {url}")
                    await process_and_store_document(url, result.markdown_v2.raw_markdown)
                    success_count += 1
                else:
                    print(f"Failed to crawl {url}: {result.error_message}")
                    fail_count += 1
                
                # Rate limiting
                await asyncio.sleep(1)
        
        print(f"\nCrawling Summary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")
        
    finally:
        print("\nClosing crawler...")
        await crawler.close()

async def main():
    """Main entry point for the crawler."""
    print("Starting Tiled documentation crawler...")
    urls = await get_tiled_docs_urls()
    await crawl_parallel(urls)

if __name__ == "__main__":
    asyncio.run(main())
