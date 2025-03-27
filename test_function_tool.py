from agents import FunctionTool
import inspect

print("Inspecting FunctionTool class:")
print(inspect.signature(FunctionTool.__init__))

# Let's create a simple function
async def add_numbers(a: int, b: int) -> int:
    """Add two numbers together
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of the two numbers
    """
    return a + b

# Try creating a FunctionTool
print("\nTrying to create a FunctionTool:")
try:
    tool = FunctionTool(add_numbers)
    print("Success! Created tool:", tool)
except Exception as e:
    print(f"Error: {e}")
    
# Try other ways of creating the tool
print("\nTrying alternative ways to create a FunctionTool:")
try:
    tool = FunctionTool(name="add", fn=add_numbers)
    print("Success with name and fn!")
except Exception as e:
    print(f"Error with name and fn: {e}")
    
try:
    tool = FunctionTool(add_numbers, name="add")
    print("Success with positional function and name!")
except Exception as e:
    print(f"Error with positional function and name: {e}") 