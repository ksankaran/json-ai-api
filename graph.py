import os
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AnyMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from enum import Enum
from langchain_core.messages import SystemMessage, HumanMessage
from tools import get_weather_forecast

tools = [
    get_weather_forecast,
]

zero_shot_prompt = PromptTemplate.from_template("""You are a helpful assistant that provides weather information.
If the user asks about the weather, use the tool to get the forecast.
If not, respond with a message indicating that you can only provide weather information.
User query: {query}
""")

class ResponseType(str, Enum):
  WEATHER = "weather"
  MESSAGE = "message"

class WeatherResponse(BaseModel):
  """Respond to the user with this"""
  response_type: ResponseType
  error: str
  temperature: float = Field(description="The temperature in fahrenheit")
  wind_direction: str = Field(
      description="The direction of the wind in abbreviated form"
  )
  wind_speed: float = Field(description="The speed of the wind in km/h")

class State(TypedDict):
  """
  Represents the state of the agent.
  """
  messages: Annotated[list[AnyMessage], add_messages]
  final_response: WeatherResponse

def respond(state: State):
  # We call the model with structured output in order to return the same format to the user every time
  # state['messages'][-2] is the last ToolMessage in the convo, which we convert to a HumanMessage for the model to use
  # We could also pass the entire chat history, but this saves tokens since all we care to structure is the output of the tool
  model = ChatOpenAI(model="gpt-4o-mini")
  model_with_structured_output = model.with_structured_output(WeatherResponse)
  response = model_with_structured_output.invoke(
    [HumanMessage(content=state["messages"][-1].content)]
  )
  print("Response: ", response)
  # We return the final answer
  return {"final_response": response}

# Define the function that determines whether to continue or not
def should_continue(state: State):
  messages = state["messages"]
  last_message = messages[-1]
  # If there is no function call, then we respond to the user
  if not last_message.tool_calls:
    return "respond"
  # Otherwise if there is, we continue
  else:
    return "continue"

def chatbot(state: State) -> dict:
  """
  Contacts LLM to get a response based on the current state.
  Args:
      state (State): The current state of the agent.
  Returns:
      dict: The updated state with the response.
  """
  model = ChatOpenAI(model="gpt-4o-mini")
  model_with_tools = model.bind_tools(tools)
  messages = state["messages"]
  
  # Always include system message with JSON formatting instructions
  system_msg = SystemMessage(content="""You are a helpful assistant that provides weather information. If the user asks about the weather, use the tool to get the forecast.""")
  
  # Combine system message with conversation messages
  # all_messages = [system_msg] + messages
  # response = model_with_tools.invoke(all_messages)
  chain = {"query": RunnablePassthrough()} | zero_shot_prompt | model_with_tools
  response = chain.invoke(messages)
  
  return {"messages": [response]}

builder = StateGraph(State)

builder.add_node('chatbot', chatbot)
builder.add_node("respond", respond)
builder.add_node("tools", ToolNode(tools))

# We now add a conditional edge
builder.add_conditional_edges(
    "chatbot",
    should_continue,
    {
        "continue": "tools",
        "respond": "respond",
    },
)
builder.add_edge("tools", "chatbot")
builder.add_edge(START, "chatbot")
builder.add_edge("respond", END)

graph = builder.compile()
