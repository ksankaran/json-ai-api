from fastapi import FastAPI
from pydantic import BaseModel
from graph import graph
#import AIMessage
from langchain_core.messages import AIMessage
import json

class ChatRequest(BaseModel):
	user_input: str
	thread_id: str = "default_thread" # For persistent conversations

# Create a FastAPI instance
app = FastAPI()

# Define a path operation for the root URL ("/") that handles GET requests
@app.post("/chat")
def chat(request: ChatRequest):
	response = graph.invoke(
		{"messages": [{ "role": "user", "content": request.user_input} ]},
		config={"configurable": {"thread_id": request.thread_id}}
	)

	final_response = response["final_response"]
	if final_response.response_type == "weather":
		# create new dict with everything from final_response except error
		response = {
			"temperature": final_response.temperature,
			"wind_direction": final_response.wind_direction,
			"wind_speed": final_response.wind_speed
		}
		return {"status": "success", "response": response }
	else:
		return {"status": "failure", "response": final_response.error }
