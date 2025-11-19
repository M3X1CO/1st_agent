import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    """
    Executes a Python file in a specified working directory.
    
    Args:
        working_directory: The base directory to scope execution to
        file_path: The path to the Python file (relative to working_directory)
        args: Optional list of command-line arguments to pass to the script
    
    Returns:
        String containing the execution output (stdout/stderr),
        or an error message string
    """
    # Get absolute paths for security check
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    
    # Security check: ensure file is within working directory
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    # Check if file exists
    if not os.path.exists(target_file):
        return f'Error: File "{file_path}" not found.'
    
    # Check if file is a Python file
    if not file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    
    # Execute the Python file
    try:
        # Build the command
        cmd = ['python', file_path] + args
        
        # Run the subprocess with timeout and capture output
        completed_process = subprocess.run(
            cmd,
            cwd=abs_working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Format the output
        output_parts = []
        
        if completed_process.stdout:
            output_parts.append(f"STDOUT:\n{completed_process.stdout}")
        
        if completed_process.stderr:
            output_parts.append(f"STDERR:\n{completed_process.stderr}")
        
        # Check for non-zero exit code
        if completed_process.returncode != 0:
            output_parts.append(f"Process exited with code {completed_process.returncode}")
        
        # If no output was produced
        if not output_parts:
            return "No output produced."
        
        return "\n".join(output_parts)
    
    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional command-line arguments, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of command-line arguments to pass to the Python script.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)
