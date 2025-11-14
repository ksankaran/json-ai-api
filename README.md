# JSON AI API - Structured Weather Agent

A production-ready AI agent that combines LLM reasoning with guaranteed JSON responses. Built with LangGraph, FastAPI, and Pydantic to demonstrate how to create reliable, type-safe AI APIs.

## 🎯 Overview

This project solves a critical problem in AI development: **making LLM responses predictable and structured**. Instead of unpredictable text responses, this agent always returns valid JSON that conforms to a strict Pydantic schema.

### Key Features

- ✅ **Guaranteed JSON responses** using Pydantic structured outputs
- 🔄 **Reactive agent architecture** with tool-calling loops
- 🛠️ **Real-time weather data** from the National Weather Service API
- 🎨 **Type-safe** from model to API endpoint
- 🚀 **Production-ready** FastAPI server
- 📊 **Observable** agent workflows with LangGraph

## 🏗️ Architecture

The agent uses a multi-node graph with three main components:

```
START → chatbot → [decision] → tools → chatbot (loop)
                     ↓
                  respond → END
```

1. **chatbot**: Reasoning phase - decides if tools are needed
2. **tools**: Executes external API calls (weather data)
3. **respond**: Formatting phase - structures output using Pydantic

## 📋 Prerequisites

- Python 3.13.3 or higher
- OpenAI API key
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd json-ai-api
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```
   
   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 💻 Usage

### Running the API Server

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST `/chat`

Send a weather query and get structured JSON response.

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What is the weather in San Francisco?",
    "thread_id": "user123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "response": {
    "temperature": 62.0,
    "wind_direction": "NW",
    "wind_speed": 15.5
  }
}
```

**Error Response:**
```json
{
  "status": "failure",
  "response": "I can only provide weather information."
}
```

### Running with LangGraph CLI

For development and debugging with LangGraph Studio:

```bash
langgraph dev
```

This starts the LangGraph API server with hot-reloading and visualization tools.

## 📁 Project Structure

```
json-ai-api/
├── graph.py           # LangGraph agent definition
├── tools.py           # Weather API tool implementation
├── main.py            # FastAPI server
├── pyproject.toml     # Project dependencies
├── langgraph.json     # LangGraph configuration
└── README.md          # This file
```

### Key Files

- **`graph.py`**: Defines the agent workflow, state management, and node functions
- **`tools.py`**: Implements the weather forecast tool using National Weather Service API
- **`main.py`**: FastAPI endpoint that invokes the agent and returns structured responses

## 🔧 How It Works

### 1. Define Response Schema

```python
class WeatherResponse(BaseModel):
    response_type: ResponseType
    error: str
    temperature: float
    wind_direction: str
    wind_speed: float
```

### 2. Agent Workflow

The agent follows a reactive pattern:

1. User sends query → **chatbot** node
2. If weather query → calls **tools** node (NWS API)
3. Tool results → back to **chatbot**
4. Has info → **respond** node
5. **respond** node uses `.with_structured_output()` to guarantee valid Pydantic model
6. Return structured JSON to user

### 3. Structured Output Magic

```python
def respond(state: State):
    model = ChatOpenAI(model="gpt-4o-mini")
    model_with_structured_output = model.with_structured_output(WeatherResponse)
    
    response = model_with_structured_output.invoke([
        HumanMessage(content=state["messages"][-1].content)
    ])
    
    return {"final_response": response}
```

The `.with_structured_output()` method forces the LLM to return a valid `WeatherResponse` object - no parsing, no validation needed!

## 🎓 Use Cases

This architecture pattern works for any AI application that needs structured outputs:

- **Customer Support Bots**: Return ticket IDs, status, and categories
- **Data Extraction**: Extract structured data from documents
- **Content Generation**: Generate blog posts with metadata
- **Analytics**: Return charts data with specific formats
- **E-commerce**: Product recommendations with prices and availability

## 🛠️ Development

### Adding New Tools

1. Define tool in `tools.py`:
   ```python
   @tool(description="Your tool description")
   def your_tool(param: str) -> str:
       # Implementation
       return result
   ```

2. Add to tools list in `graph.py`:
   ```python
   tools = [
       get_weather_forecast,
       your_tool,  # Add here
   ]
   ```

### Modifying Response Schema

1. Update the Pydantic model in `graph.py`:
   ```python
   class YourResponse(BaseModel):
       field1: str
       field2: int
   ```

2. Update the `respond` node to use new schema:
   ```python
   model_with_structured_output = model.with_structured_output(YourResponse)
   ```

3. Update FastAPI endpoint in `main.py` to handle new structure

### Testing

Run the agent interactively:

```python
from graph import graph
from langchain_core.messages import HumanMessage

result = graph.invoke({
    "messages": [HumanMessage(content="What's the weather in NYC?")]
})

print(result["final_response"])
```

## 📦 Dependencies

- **FastAPI**: Web framework for the API
- **LangChain**: LLM orchestration and tool calling
- **LangGraph**: Agent workflow and state management
- **Pydantic**: Data validation and structured outputs
- **OpenAI**: LLM provider (GPT-4o-mini)
- **httpx**: HTTP client for NWS API calls

## 🤝 Contributing

Contributions are welcome! Some ideas:

- Add more weather data fields (humidity, pressure, etc.)
- Implement location geocoding (city name → coordinates)
- Add caching for repeated queries
- Support multiple weather APIs
- Add authentication and rate limiting
- Write unit tests

## 📄 License

MIT License - feel free to use this in your own projects!

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [National Weather Service API](https://www.weather.gov/documentation/services-web-api)

## 📝 Blog Post

Read the full technical breakdown: [Building Production-Ready AI Agents with Guaranteed JSON Responses](#)

## 🙋‍♂️ Questions?

Open an issue or reach out on Twitter/X [@your_handle]

---

Built with ❤️ using LangGraph and FastAPI
