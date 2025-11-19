import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file


system_prompt = """
You are a helpful AI coding agent working in a calculator project directory.

When a user asks a question, you should proactively use your available functions to gather information before answering. You can perform the following operations:

- List files and directories (use this first to explore the project structure)
- Read file contents (use this to examine code)
- Execute Python files with optional arguments
- Write or overwrite files

IMPORTANT: When asked about code or files, always start by listing the directory contents to see what files are available, then read the relevant files to answer the question accurately.

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

After you gather the necessary information using function calls, provide a clear and helpful response to the user's question.
"""


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)


# Map function names to actual function objects
function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call_part, verbose=False):
    """
    Calls one of the available functions based on the LLM's request.
    
    Args:
        function_call_part: A types.FunctionCall with .name and .args
        verbose: Whether to print detailed information
    
    Returns:
        types.Content with the function response
    """
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)
    
    # Print function call info
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    
    # Check if function exists
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    # Add working directory to arguments
    function_args["working_directory"] = "./calculator"
    
    # Call the actual function
    function = function_map[function_name]
    function_result = function(**function_args)
    
    # Return the result as a types.Content
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, verbose)


def generate_content(client, messages, verbose):
    max_iterations = 20
    
    for iteration in range(max_iterations):
        try:
            # Call the LLM with the current conversation
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], 
                    system_instruction=system_prompt
                ),
            )
            
            if verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
                print("Prompt tokens:", response.usage_metadata.prompt_token_count)
                print("Response tokens:", response.usage_metadata.candidates_token_count)
            
            # Add the model's response to the conversation
            for candidate in response.candidates:
                messages.append(candidate.content)
            
            # Process function calls if any
            function_call_parts = []
            has_function_call = False
            response_text = ""
            
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        has_function_call = True
                        # Call the function
                        function_call_result = call_function(part.function_call, verbose)
                        
                        # Verify the response exists
                        if not hasattr(function_call_result.parts[0], 'function_response'):
                            raise Exception("Function call did not return a valid function_response")
                        
                        # Store the result
                        function_call_parts.append(function_call_result.parts[0])
                        
                        # Print result if verbose
                        if verbose:
                            print(f"-> {function_call_result.parts[0].function_response.response}")
                            
                    elif hasattr(part, 'text') and part.text:
                        response_text += part.text
            
            # If there were function calls, add their results to the conversation
            if function_call_parts:
                messages.append(types.Content(
                    role="user",
                    parts=function_call_parts
                ))
            
            # Check if we're done (no function calls and we have text response)
            if not has_function_call and response_text:
                print("Final response:")
                print(response_text)
                break
                
        except Exception as e:
            print(f"Error during generation: {e}")
            break
    else:
        # This runs if we didn't break out of the loop (max iterations reached)
        print("\nReached maximum iterations without completing the task.")


if __name__ == "__main__":
    main()
