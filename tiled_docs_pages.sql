-- Drop existing objects
drop function if exists match_tiled_docs(vector(1536), integer, jsonb) cascade;
drop index if exists idx_tiled_docs_metadata;
drop table if exists tiled_docs_pages cascade;

-- Enable the pgvector extension if not already enabled
create extension if not exists vector;

-- Create the Tiled documentation chunks table
create table tiled_docs_pages (
    id bigserial primary key,
    url varchar not null,
    chunk_number integer not null,
    title varchar not null,
    summary varchar not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,  -- Stores category, features, file_formats, version_info
    embedding vector(1536),
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
    -- Add a unique constraint to prevent duplicate chunks
    unique(url, chunk_number)
);

-- Create an index for better vector similarity search performance
create index on tiled_docs_pages using ivfflat (embedding vector_cosine_ops);

-- Create an index on metadata for faster filtering
create index idx_tiled_docs_metadata on tiled_docs_pages using gin (metadata);

-- Create a function to search for Tiled documentation chunks
create or replace function match_tiled_docs (
  query_embedding vector(1536),
  match_count int default 10,
  filter jsonb DEFAULT '{}'::jsonb
) returns table (
  id bigint,
  url varchar,
  chunk_number integer,
  title varchar,
  summary varchar,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    url,
    chunk_number,
    title,
    summary,
    content,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from tiled_docs_pages
  where case
    when filter != '{}'::jsonb then
      metadata @> filter
    else
      true
    end
  order by embedding <=> query_embedding
  limit match_count;
end;
$$;
