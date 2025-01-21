-- Create conversations table
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

-- Create index on conversation_id for faster lookups
create index idx_tiled_conversations_conversation_id on tiled_conversations(conversation_id);

-- Create index on user_id for faster lookups
create index idx_tiled_conversations_user_id on tiled_conversations(user_id);

-- Enable Row Level Security
alter table tiled_conversations enable row level security;

-- Create policy to allow insert for authenticated users
create policy "Allow insert for authenticated users"
    on tiled_conversations for insert
    with check (auth.role() = 'authenticated');

-- Create policy to allow select for authenticated users
create policy "Allow select for authenticated users"
    on tiled_conversations for select
    using (auth.role() = 'authenticated');

-- Create policy to allow update for authenticated users
create policy "Allow update for authenticated users"
    on tiled_conversations for update
    using (auth.role() = 'authenticated');
