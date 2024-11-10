''''
Let's build the graph of the ReACT agent manually in LangGraph.
Also track the tool calls and the agent's thought process!
'''

import os
from typing import TypedDict, Annotated
import operator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.messages import HumanMessage
from rich.console import Console
from PIL import Image as PILImage
import ipdb
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
# initialize dotenv to load environment variables
load_dotenv()

#Rich initialize
rich= Console()

tool = TavilySearchResults(max_results=2)
# print(type(tool))
# print(tool.name)

# memory = SqliteSaver.from_conn_string(":memory:")
checkpointer = MemorySaver()
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class Agent:

    def __init__(self, model, tools, checkpointer: BaseCheckpointSaver, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            if not t['name'] in self.tools:      # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print("Back to the model!")
        return {"messages":results}


prompt= """
You are a smart research assistant. Use the search engine to look up information.
You are allowed to make multiple calls (either together or in sequence).
Only look up information when you are sure of what you want.
If you need to look up some information before asking a follow up question, you are allowed to do that!

"""

model = ChatOpenAI(model="gpt-4-turbo")
abot= Agent(model, [tool], checkpointer=checkpointer, system=prompt )
png_data = abot.graph.get_graph().draw_png()
with open("graph.png", "wb") as f:
    f.write(png_data)
# save the graph for visualization
img = PILImage.open("graph.png")
# img.show()


# After creating the agent (abot)
thread = {"configurable":{"thread_id":"1"}}  # Keep track of conversation

def chat_loop():
    rich.print("[bold blue]Chat with AI Assistant (type 'quit' to exit)[/bold blue]")
    
    while True:
        # Get user input
        user_input = input("\n[You]: ").strip()
        
        # Check for quit command
        if user_input.lower() == 'quit':
            rich.print("[bold red]Ending chat session...[/bold red]")
            break
        
        # Create message and process through graph
        messages = [HumanMessage(content=user_input)]
        
        rich.print("\n[bold green]Assistant:[/bold green]")
        # Stream the response
        for event in abot.graph.stream({"messages": messages}, thread):
            for v in event.values():
                rich.print(v)
        
        print("\n" + "-"*50)  # Add a separator between conversations

# Start the chat loop
if __name__ == "__main__":
    chat_loop()







