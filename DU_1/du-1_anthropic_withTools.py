import os
import anthropic
import json
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# ── Tool definitions (what the model "sees") ──────────────────────────────────
tools = [
    {
        "name": "calculator",
        "description": "Performs basic math operations: add, subtract, multiply, divide, power, sqrt.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt"]
                },
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number (not needed for sqrt)"}
            },
            "required": ["operation", "a"]
        }
    },
    {
        "name": "text_analyzer",
        "description": "Analyzes a text string: counts words, characters, sentences.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "unit_converter",
        "description": "Converts between units: km/miles, celsius/fahrenheit, kg/pounds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "from_unit": {"type": "string", "enum": ["km", "mm", "miles", "celsius", "fahrenheit", "kg", "pounds"]},
                "to_unit":   {"type": "string", "enum": ["km", "mm", "miles", "celsius", "fahrenheit", "kg", "pounds"]}
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    },
    {
        "name": "current_time",
        "description": "Returns the current date and time in ISO format.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


# ── Actual Python implementations ─────────────────────────────────────────────
def text_analyzer(text):
    return {
        "characters": len(text),
        "words":      len(text.split()),
        "sentences":  text.count('.') + text.count('!') + text.count('?')
    }

def unit_converter(value, from_unit, to_unit):
    conversions = {
        ("km",         "miles"):      lambda v: v * 0.621371,
        ("miles",      "km"):         lambda v: v * 1.60934,
        ("celsius",    "fahrenheit"): lambda v: v * 9/5 + 32,
        ("fahrenheit", "celsius"):    lambda v: (v - 32) * 5/9,
        ("kg",         "pounds"):     lambda v: v * 2.20462,
        ("pounds",     "kg"):         lambda v: v * 0.453592,
        ("km",         "mm"):         lambda v: v * 1e6,
        ("mm",         "km"):         lambda v: v / 1e6,
    }
    fn = conversions.get((from_unit, to_unit))
    return {"result": fn(value), "from": f"{value} {from_unit}", "to": f"{fn(value):.4f} {to_unit}"} \
           if fn else {"error": f"Conversion {from_unit} --> {to_unit} not supported"}

def current_time():
    return {"current_time": datetime.now().isoformat()} 

def calculator(operation, a, b=None):
    ops = {
        "add":      lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide":   lambda: a / b if b != 0 else "Error: division by zero",
        "power":    lambda: a ** b,
        "sqrt":     lambda: math.sqrt(a)
    }
    return {"result": ops[operation]()}


available_tools = {
    "calculator": calculator,
    "current_time": current_time,
    "text_analyzer": text_analyzer,
    "unit_converter": unit_converter
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────
def run_tool(name, inputs):
    registry = {
        "calculator": calculator,
        "current_time": current_time,
        "text_analyzer":  text_analyzer,
        "unit_converter": unit_converter,
    }
    fn = registry.get(name)
    return json.dumps(fn(**inputs) if fn else {"error": f"Unknown tool: {name}"})

# ── Agentic loop ──────────────────────────────────────────────────────────────
def run_agent(user_message: str):
    print(f"\nUser message: {user_message}")
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # Collect any tool calls in this response
        tool_results = []
        #print(f"Response content blocks: {response.content}")
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> Tool call: {block.name}({block.input})")
                result = run_tool(block.name, block.input)
                print(f"  <- Result:    {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # If the model called tools, feed results back and loop
        if tool_results:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user",      "content": tool_results})
            continue

        # No tool calls → final answer
        final = next((b.text for b in response.content if hasattr(b, "text")), "")
        print(f"\nAssistant: {final}")
        return final

# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_agent("What is the square root of 142, what is the square root of 25 and what time is it now?")
    #run_agent("Convert 100 km to milimeters, then convert 37 celsius to fahrenheit.")
    run_agent("Convert 100 km to pounds, then convert 37 celsius to fahrenheit.")
    #run_agent("Analyze this text: 'Hello world. How are you? I am fine!'")

