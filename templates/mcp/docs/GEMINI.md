# Tool Development Guidelines

This document outlines the best practices for developing tools for the MCP server.

**IMPORTANT:** Your responsibility is to write the tool module itself. **Do not** create a runnable tool server script (e.g., `tool_server.py`). The environment you are developing for already has a server to load and run your tool.
DO NOT TRY TO CREATE, OR EDIT ANY FILE OTHER THAN EXACTLY ONLY THE TOOL YOU ARE WORKING ON! YOU ARE NOT ALLOWED TO EDIT THE SERVER OR THE MCP_INSTANCE FILES! THESE FILES ARE BEYOND YOUR SCOPE!
ONCE YOU HAVE EDITED THE TOOL, DO NOT TRY TO RUN IT! YOU ARE NOT IN AN ENVIRONMENT WHERE YOU CAN RUN THE TOOLS YOU CREATE. A TOOL SERVER RESTART IS REQUIRED.

IMPORTANT::::::::::::: This is the most important instruction of all. Are you paying attention:
EACH TIME:
AFTER YOU HAVE EDITED CODE, REVIEW THE CODE AND GIVE IT CRITIQUE/FEEDBACK FOR IMPROVEMENTS. I need you to ACTUALLY use the "read file" tool each time so that you actually get the correct and up-to-date file. Do this each time when you believe your work is done. And I need you to be critical to the work done in the file and consider if it's implemented the best way possible.

## Core Architecture

To avoid past issues with circular dependencies, the architecture relies on a central, shared `mcp` instance.

1.  **Central `mcp` Instance:** A central `mcp` object is defined in **`tools/mcp_instance.py`**. All tools **must** import this single instance to ensure they register correctly with the running server.
2.  **Self-Registration:** Tool modules are responsible for their own registration via the `<!-- Import failed: mcp.tool()` - Only .md files are supported --> decorator, which is imported from the central instance.

---

## Creating or editing a Tool (The Right Way)
1.  Create a new Python file inside a relevant subdirectory within `tools/mcp/category_directory` (e.g., `tools/mcp/web/`, `tools/mcp/utility/`). This helps organize tools logically.
2.  Import the shared `mcp` object: `from tools.mcp_instance import mcp`.
3.  Import `Field` from `pydantic`: `from pydantic import Field`.
4.  Write your tool's logic as an `async` function.
5.  Decorate the function with `@mcp.tool()`, providing a clear `description`.
6.  Use standard Python type hints and `pydantic.Field` for rich, descriptive parameters.
7. Post-Modification Check: After any replace or write_file operation, I will now explicitly check if the modified file is a tool definition.
8. Mandatory Pause: If a tool definition is modified, I will mandatorily pause any subsequent tool execution attempts and immediately inform you about the server restart requirement, as per the guidelines.

## Writing guidelines

1. Write descriptive tool names, titles and descriptions. Instead of calling a tool "wikipedia", it should be called "wikipedia_search", or similar. Think of this step as SEO, make sure it's easily digestible by only looking at the title. Having a tool called "search" is bad, but one called "image_search_unsplash_stock_photo" is good. It's EXPLICIT.
2. Think of all kinds of settings you can expose as input parameters. Do not make "the simplest version", think before you act and make it an amazing tool!
3. Use clear and descriptive file names, tool names, and property names. This is how LLMs will interface, by reading the name and description. Make them "generic and search-friendly", but still specific enough. Example names: `/web/search_google` is a good name, it's a web tool, and it is a search tool, and then google is the class of search tool. Just naming it 'google' is bad, because it could be many things.
4. Do not add print strings or logs in the code. This will just print on the server and it spams the tool server.
5. **Document your return values.** Write clear and descriptive documentation for your tool's return values. This will help the AI understand what to expect from your tool and how to use the results.


## Coding Guidelines
1. Variables, like API keys and other "user settings" should be exposed at the top of the script like variables. NOT ENVIRONMENTAL VARIABLES
2. Make sure to tell the user about the variables created when making a tool after it's done, so the user can fill the variables with data.
3. Do not use dict description as code comments! Do not add sample code, do not add notes about work done or notes for the user. All descriptions, including the ) -> dict: """ Tool summary """, is meant to give information and context for the language model using the tool in the future. That's all this should be. It should be explicit so it's clear how the tool can be used, and it should include all context needed.
4. Use the return values as a way to instruct the language model using the tool. Return follow-up instructions as a return value to make the LLM understand the intended flow better. Inform it about the next step, or how to present the results to the user. Use a "next_action" return value for this.
5. **USE RETURN VALUES TO YOUR ADVANTAGE** All actions should return relevant information to the LLM and the user. The best way of doing this is to use a return_value filled with relevant information. It should include the actions taken, and results relevant to the user. It should also include instructions to the language model on the next step. It should include the modified data to the user. This provides transparency and allows the user to see the result of the action they've taken. For example, if a tool creates a new project, it should return the created project object. If a tool edits an entry in a file, the relevant edits should be returned, and if we want the LLM to act in a specific way, such as presenting the results to the user, this should be included here.

## Guiding the AI
Guiding the AI with Return Values

One powerful technique for building effective tools is to use the return value to guide the AI on what to do next. This is especially important for tools that require multiple steps or user interaction. By providing clear, step-by-step instructions in the return value, you can ensure that the AI uses your tool correctly and provides a smooth, intuitive experience for the user.

The next_action Field

The best way to guide the AI is to include a next_action field in your tool's return value. This field should be a string that contains a clear, step-by-step guide for the AI.

Example: The `study_buddy` Tool

Let's look at the study_buddy tool as an example. The create_project mode in this tool is the first step in a multi-step workflow. Here's how it uses the next_action field to guide the AI in study_buddy.py:

if mode == 'create_project':
    # ... (create the project)

    return {
        "status": f"Project '{project_name}' created successfully.",
        "next_action": f"The project has been created. Now, you need to generate the lessons for the course.\\n\\n1. **Propose the number of lessons:** Propose {default_lesson_counts[project_type]} lessons to the user.\\n2. **Ask for confirmation:** Ask the user to confirm this number or provide a different one.\\n3. **Propose different ways to generate the curriculum:** Ask the user how they would like to create the course curriculum. For example: 'How would you like to create the course curriculum? Should I use my own knowledge? Should I try to search the web, or should we perhaps use another tool like [TOOL X] if you have one in mind?'\\n4. **Generate the lessons:** Once the user has confirmed the number of lessons and the source of knowledge, generate the lessons. Each lesson should be a dictionary that conforms to the lesson type's schema: {lesson_definitions[project_type]}\\n5. **Add the lessons to the project:** Use the `add_lessons` mode to add the generated lessons to the project."}

The AI's Workflow

When the AI receives this return value, it knows exactly what to do next:

1. Inform the user: The AI will inform the user that the project has been created.
2. Propose the number of lessons: The AI will propose the default number of lessons to the user.
3. Ask for confirmation: The AI will ask the user to confirm the number of lessons.
4. Ask for the source of knowledge: The AI will ask the user how they want to generate the curriculum.
5. Generate the lessons: The AI will generate the lessons based on the user's input.
6. Call the `add_lessons` tool: The AI will call the add_lessons tool to add the generated lessons to the project.

By providing these clear, step-by-step instructions, we can ensure that the AI follows the correct workflow and provides a seamless experience for the user.

Key Takeaways:

* Use the return value to guide the AI.
* Use a next_action field to provide clear, step-by-step instructions.
* Be explicit and detailed in your instructions.
* Think about the entire workflow and provide instructions for each step.

### Common Pitfalls & Important Notes

*   **File Paths in Code:** When defining file paths as strings in your Python code, **always use forward slashes (`/`)** instead of backslashes (``). Backslashes can be misinterpreted as escape characters on Windows, leading to a `(unicode error) 'unicodeescape' codec can't decode bytes...` error when the tool is loaded. Forward slashes are compatible with all major operating systems.
    *   **Correct:** `my_path = "my_folder/my_file.txt"`
    *   **Incorrect:** `my_path = "my_folder\my_file.txt"`

*   **Focus on the Tool:** To reiterate, just create the Python file containing your tool's logic. Do not add server execution logic (`if __name__ == "__main__": ...`) or create separate server files.

## Requirements & Libraries
You do not have access to the environment, you are ONLY creating the tool.
Report to the user which libraries need to be pip installed and the user will add them to requirements.txt

### Example: `generate_qr_code` Tool

This example demonstrates the current, correct standard.
Notice that there's no description inside the @mcp.tool(). DO NOT MAKE IT @mcp.tool("Description for the tool")

**File:** `tools/mcp/web/qr_code.py`

```import qrcode
from io import BytesIO
import base64
from typing import Optional, Tuple, Union
import os
from datetime import datetime
import uuid
from pydantic import Field
from tools.mcp_instance import mcp

# Any API keys or other important configurable properties should be defined here

@mcp.tool()
async def generate_qr_code(
    data: str = Field(description="The text or data to encode in the QR code."),
    version: Optional[int] = Field(None, description="The version of the QR code (1 to 40)."),
    box_size: int = Field(10, description="The size of each 'box' (pixel) in the QR code."),
    border: int = Field(4, description="The thickness of the border around the QR code."),
    fill_color: str = Field("black", description="The color of the QR code (e.g., 'red', 'rgb(255,0,0)')."),
    back_color: str = Field("white", description="The background color.")
) -> dict:
    """Generate a QR code image from input text."""
    def _parse_color(color_input: str) -> Union[str, Tuple[int, int, int]]:
        """Parses a string representation of an RGB tuple into a tuple."""
        if color_input.startswith('rgb(') and color_input.endswith(')'):
            try:
                cleaned_str = color_input.strip('rgb()')
                r, g, b = map(int, cleaned_str.split(','))
                return (r, g, b)
            except (ValueError, TypeError):
                return "black" # Default to black on parsing error
        return color_input

    try:
        parsed_fill_color = _parse_color(fill_color)
        parsed_back_color = _parse_color(back_color)

        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=parsed_fill_color, back_color=parsed_back_color)
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        
        return {"image_base64": img_str}
    
    except Exception as e:
        return {"error": f"Error generating QR code: {str(e)}"}

```

## Example script with multiple tools built into one, with a mode selector. This is preferred almost always to keep the tool count low.
**File:** `tools/mcp/utility/simple_math.py`
```
import math
from typing import Optional, List, Union, Literal
from pydantic import Field
from tools.mcp_instance import mcp

# Any API keys or other important configurable properties should be defined here

@mcp.tool()
async def simple_math(
    mode: Literal[
        'add', 'subtract', 'multiply', 'divide', 'sum', 'average', 'min', 'max',
        'floor', 'ceil', 'round', 'sqrt', 'power', 'abs', 'mod', 'log'
    ] = Field(description="The mathematical operation to perform."),
    num1: Optional[Union[int, float]] = Field(None, description="First number. (modes: add, subtract, multiply, divide, mod)"),
    num2: Optional[Union[int, float]] = Field(None, description="Second number. (modes: add, subtract, multiply, divide, mod)"),
    numbers: Optional[List[Union[int, float]]] = Field(None, description="List of numbers. (modes: sum, average, min, max)"),
    number: Optional[Union[int, float]] = Field(None, description="Single number. (modes: floor, ceil, round, sqrt, abs, log)"),
    decimals: Optional[int] = Field(None, description="Number of decimal places for rounding. (mode: round)"),
    base: Optional[Union[int, float]] = Field(None, description="Base for power or logarithm. (modes: power, log)"),
    exponent: Optional[Union[int, float]] = Field(None, description="Exponent for power. (mode: power)")
) -> dict:
    """
    Performs various simple mathematical operations.
    - add: Adds two numbers. Needs: num1, num2.
    - subtract: Subtracts num2 from num1. Needs: num1, num2.
    - multiply: Multiplies two numbers. Needs: num1, num2.
    - divide: Divides num1 by num2. Needs: num1, num2.
    - sum: Calculates the sum of a list of numbers. Needs: numbers.
    - average: Calculates the average of a list of numbers. Needs: numbers.
    - min: Finds the minimum value in a list of numbers. Needs: numbers.
    - max: Finds the maximum value in a list of numbers. Needs: numbers.
    - floor: Returns the largest integer less than or equal to a number. Needs: number.
    - ceil: Returns the smallest integer greater than or equal to a number. Needs: number.
    - round: Rounds a number to a specified number of decimals. Needs: number, (optional) decimals.
    - sqrt: Calculates the square root of a number. Needs: number.
    - power: Raises a base to an exponent. Needs: base, exponent.
    - abs: Returns the absolute value of a number. Needs: number.
    - mod: Calculates the remainder of num1 divided by num2. Needs: num1, num2.
    - log: Calculates the logarithm of a number to a given base (default e). Needs: number, (optional) base.
    """
    result = None
    error = None

    try:
        if mode == 'add':
            if num1 is None or num2 is None: raise ValueError("num1 and num2 are required for 'add' mode.")
            result = num1 + num2
        elif mode == 'subtract':
            if num1 is None or num2 is None: raise ValueError("num1 and num2 are required for 'subtract' mode.")
            result = num1 - num2
        elif mode == 'multiply':
            if num1 is None or num2 is None: raise ValueError("num1 and num2 are required for 'multiply' mode.")
            result = num1 * num2
        elif mode == 'divide':
            if num1 is None or num2 is None: raise ValueError("num1 and num2 are required for 'divide' mode.")
            if num2 == 0: raise ValueError("Division by zero is not allowed.")
            result = num1 / num2
        elif mode == 'sum':
            if not isinstance(numbers, list): raise ValueError("numbers (list) is required for 'sum' mode.")
            result = sum(numbers)
        elif mode == 'average':
            if not isinstance(numbers, list) or not numbers: raise ValueError("numbers (non-empty list) is required for 'average' mode.")
            result = sum(numbers) / len(numbers)
        elif mode == 'min':
            if not isinstance(numbers, list) or not numbers: raise ValueError("numbers (non-empty list) is required for 'min' mode.")
            result = min(numbers)
        elif mode == 'max':
            if not isinstance(numbers, list) or not numbers: raise ValueError("numbers (non-empty list) is required for 'max' mode.")
            result = max(numbers)
        elif mode == 'floor':
            if number is None: raise ValueError("number is required for 'floor' mode.")
            result = math.floor(number)
        elif mode == 'ceil':
            if number is None: raise ValueError("number is required for 'ceil' mode.")
            result = math.ceil(number)
        elif mode == 'round':
            if number is None: raise ValueError("number is required for 'round' mode.")
            result = round(number, decimals) if decimals is not None else round(number)
        elif mode == 'sqrt':
            if number is None: raise ValueError("number is required for 'sqrt' mode.")
            if number < 0: raise ValueError("Cannot calculate square root of a negative number.")
            result = math.sqrt(number)
        elif mode == 'power':
            if base is None or exponent is None: raise ValueError("base and exponent are required for 'power' mode.")
            result = math.pow(base, exponent)
        elif mode == 'abs':
            if number is None: raise ValueError("number is required for 'abs' mode.")
            result = abs(number)
        elif mode == 'mod':
            if num1 is None or num2 is None: raise ValueError("num1 and num2 are required for 'mod' mode.")
            if num2 == 0: raise ValueError("Modulo by zero is not allowed.")
            result = num1 % num2
        elif mode == 'log':
            if number is None: raise ValueError("number is required for 'log' mode.")
            if number <= 0: raise ValueError("Logarithm is undefined for non-positive numbers.")
            result = math.log(number, base) if base is not None else math.log(number)
        else:
            error = f"Invalid mode: {mode}"
    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"An unexpected error occurred: {str(e)}"

    if error:
        return {"error": error}
    else:
        return {"result": result}
```