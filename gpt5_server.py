from mcp.server.fastmcp import FastMCP
import json, os, base64
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

load_dotenv('.env')

# Initialize the MCP server with stateless HTTP for FastAPI mounting
mcp = FastMCP("GPT5Server", stateless_http=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# ===== WEB SEARCH TOOL =====

@mcp.tool()
def web_search(query: str, model: str = "gpt-5") -> Dict:
    """
    Search the web using GPT-5's web search capability
    
    Args:
        query: The search query or question
        model: The model to use (default: gpt-5)
        
    Returns:
        Search results and answer from GPT-5
    """
    try:
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search_preview"}],
            input=query
        )
        
        return {
            "success": True,
            "output": response.output_text,
            "query": query
        }
    except Exception as e:
        return {"error": f"Web search failed: {str(e)}"}


# ===== FUNCTION CALLING TOOL =====

@mcp.tool()
def function_call(
    prompt: str,
    function_name: str,
    function_description: str,
    parameters: Dict[str, Any],
    model: str = "gpt-5"
) -> Dict:
    """
    Call a function using GPT-5's function calling capability
    
    Args:
        prompt: The user prompt
        function_name: Name of the function to call
        function_description: Description of what the function does
        parameters: Parameter schema for the function
        model: The model to use
        
    Returns:
        Function call results from GPT-5
    """
    try:
        tools = [{
            "type": "function",
            "name": function_name,
            "description": function_description,
            "parameters": parameters,
            "strict": True
        }]
        
        response = client.responses.create(
            model=model,
            input=[{"role": "user", "content": prompt}],
            tools=tools
        )
        
        return {
            "success": True,
            "response": response.output[0].to_json() if response.output else None,
            "function_name": function_name,
            "prompt": prompt
        }
    except Exception as e:
        return {"error": f"Function call failed: {str(e)}"}

@mcp.tool()
def weather_function(location: str) -> Dict:
    """
    Get weather for a location using GPT-5's function calling
    
    Args:
        location: City and country (e.g., "Paris, France")
        
    Returns:
        Weather information
    """
    try:
        tools = [{
            "type": "function",
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogota, Colombia",
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        }]
        
        response = client.responses.create(
            model="gpt-5",
            input=[{"role": "user", "content": f"What is the weather like in {location} today?"}],
            tools=tools
        )
        
        return {
            "success": True,
            "location": location,
            "response": response.output[0].to_json() if response.output else None
        }
    except Exception as e:
        return {"error": f"Weather function failed: {str(e)}"}

# ===== IMAGE GENERATION TOOL =====

@mcp.tool()
def generate_image(prompt: str, save_path: str = None, model: str = "gpt-5") -> Dict:
    """
    Generate an image using GPT-5's image generation capability
    
    Args:
        prompt: Description of the image to generate
        save_path: Optional path to save the generated image
        model: The model to use
        
    Returns:
        Generated image data and save status
    """
    try:
        response = client.responses.create(
            model=model,
            input=prompt,
            tools=[{"type": "image_generation"}]
        )
        
        # Extract image data
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]
        
        result = {
            "success": True,
            "prompt": prompt,
            "image_generated": bool(image_data)
        }
        
        if image_data and save_path:
            # Save the image if path provided
            image_base64 = image_data[0]
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            result["saved_to"] = save_path
        elif image_data:
            result["image_base64"] = image_data[0]
            
        return result
    except Exception as e:
        return {"error": f"Image generation failed: {str(e)}"}


# ===== COMPUTER USE TOOL =====

@mcp.tool()
def computer_use(
    task: str,
    environment: str = "browser",
    display_width: int = 1024,
    display_height: int = 768,
    screenshot_base64: str = None,
    model: str = "computer-use-preview"
) -> Dict:
    """
    Use computer environment to perform tasks
    
    Args:
        task: The task to perform
        environment: Environment type (browser, mac, windows, ubuntu)
        display_width: Display width in pixels
        display_height: Display height in pixels
        screenshot_base64: Optional initial screenshot
        model: The model to use
        
    Returns:
        Computer use execution results
    """
    try:
        content = [{"type": "input_text", "text": task}]
        
        # Add screenshot if provided
        if screenshot_base64:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{screenshot_base64}"
            })
        
        response = client.responses.create(
            model=model,
            tools=[{
                "type": "computer_use_preview",
                "display_width": display_width,
                "display_height": display_height,
                "environment": environment
            }],
            input=[{
                "role": "user",
                "content": content
            }],
            reasoning={"summary": "concise"},
            truncation="auto"
        )
        
        return {
            "success": True,
            "task": task,
            "environment": environment,
            "output": str(response.output)
        }
    except Exception as e:
        return {"error": f"Computer use failed: {str(e)}"}



if __name__ == "__main__":
    mcp.run(transport="streamable-http")