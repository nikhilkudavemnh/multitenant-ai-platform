# Q. Create a Graph where you pass the single list of integers along with name and operation. If Operation is "+" you add and if "*" you multiply the element
#     input : {"name": "Jack Donald", "value":[1,2,3], "operation":"*"}
#     output: "Hi Jack Donald , your answer is : 6"


from typing import TypedDict, List
from langgraph.graph import StateGraph
import math

class AgentState(TypedDict):
    name: str
    value: List[int]
    operation: str
    result: str


def process_operation(state: AgentState) -> AgentState:
    """this function do the operation"""
    match state["operation"]:
        case "*":
            state["result"] = f"Hi {state["name"]}, your problem answers is {math.prod(state["value"])}"
        case "+":
            state["result"] = f"Hi {state["name"]}, your problem answers is {sum(state["value"])}"
        case "-":
            return state

    return state

graph =  StateGraph(AgentState)

graph.add_node("process_value", process_operation)
graph.set_entry_point("process_value")
graph.set_finish_point("process_value")

app = graph.compile()
#
# from Ipython.display import Image, display
# display(Image(app.get_graph().draw_mermaid()))

answers = app.invoke({"name":"Nik", "value":[4,5,2], "operation":"+"})
print(answers)