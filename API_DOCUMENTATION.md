# Tiled AI Expert API Documentation

## Overview
The Tiled AI Expert API is designed to facilitate natural language conversations about the Tiled map editor. It serves as a knowledgeable agent that can understand context, maintain conversation history, and provide relevant information from the Tiled documentation.

## Base URL
```
https://tiled-expert-api-production.up.railway.app
```

## Authentication
All requests require a Bearer token in the Authorization header:
```
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

### 1. Health Check
- **GET /** 
- Returns API health status and version information

### 2. Ask Tiled Expert
- **POST /api/v1/tiled/ask**
- Main endpoint for querying the Tiled AI expert

#### Request Body
```json
{
    "query": "string",         // Required: Your question about Tiled
    "user_id": "string",      // Required: Unique identifier for the user/agent
    "conversation_id": "string" // Optional: For maintaining conversation context
}
```

#### Response Format
```json
{
    "success": boolean,
    "message": "string",
    "data": {
        "response": "string"   // Markdown-formatted response
    }
}
```

## Best Practices for Agent-to-Agent Communication

### 1. Establishing Context
When starting a conversation, provide:
- Project context (game type, requirements)
- Current development phase
- Specific challenges or goals

### 2. Iterative Questioning
- Start with broad questions to establish understanding
- Follow up with specific technical queries
- Reference previous answers in follow-up questions

### 3. Maximum Interaction Limit
- Limit conversations to 10 questions per session
- Use conversation_id to maintain context between questions

## Example Usage Scenarios

### Scenario 1: Unity Integration Agent
This example shows how a game development agent might interact with the API to understand Tiled integration with Unity.

#### Initial Query
```json
{
    "query": "I am developing a 2D RPG game in Unity and want to use Tiled for creating my game worlds. Can you explain how Tiled can integrate with Unity and what are the key considerations for this workflow?",
    "user_id": "unity_game_agent",
    "conversation_id": "unity_rpg_project_001"
}
```

The API provides detailed information about Unity integration, including map formats, tileset structures, and implementation steps.

#### Follow-up Query
```json
{
    "query": "You mentioned custom Tiled plugins for Unity integration. Can you explain more about what plugins are available and how they can help with the workflow?",
    "user_id": "unity_game_agent",
    "conversation_id": "unity_rpg_project_001"
}
```

The API provides specific information about available plugins like Tiled2Unity and TiledSharp.

### Scenario 2: Performance Optimization Agent
This example demonstrates how an optimization-focused agent might use the API to handle large maps efficiently.

#### Initial Query
```json
{
    "query": "I am working on optimizing a large open-world game that uses Tiled for map creation. What are the best practices for handling large maps in Tiled, particularly regarding memory management and performance?",
    "user_id": "optimization_agent",
    "conversation_id": "large_map_optimization_001"
}
```

The API provides detailed optimization strategies, including chunking and streaming techniques.

#### Follow-up Query
```json
{
    "query": "You mentioned using custom properties to track loaded states. Can you provide more details about custom properties in Tiled?",
    "user_id": "optimization_agent",
    "conversation_id": "large_map_optimization_001"
}
```

The API provides specific information about custom properties and their implementation.

### Scenario 3: Automation Agent
This example shows how an automation-focused agent might use the API to understand Tiled's automation capabilities.

```json
{
    "query": "I am developing an automation pipeline for our game development team. We need to automate the process of creating, validating, and exporting Tiled maps. What automation capabilities does Tiled provide?",
    "user_id": "automation_agent",
    "conversation_id": "tiled_automation_001"
}
```

The API provides information about command-line tools and Python scripting options for automation.

## Response Analysis

The API responses consistently provide:
1. Clear context acknowledgment
2. Structured information with headers
3. Code examples where relevant
4. Documentation coverage indicators
5. Source references
6. Related topics for further exploration

## Best Practices for Implementation

1. **Maintain Context**: Always use the same conversation_id for related queries
2. **Be Specific**: Provide detailed context in your queries
3. **Follow Up**: Use information from previous responses to ask more detailed questions
4. **Track Documentation**: Pay attention to the documentation coverage indicators in responses
5. **Validate Sources**: Check the provided source links for additional information
