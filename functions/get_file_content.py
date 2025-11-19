import os
from google.genai import types

MAX_CHARS = 10000


def get_file_content(working_directory, file_path):
    """
    Reads and returns the content of a file, scoped to a working directory.
    
    Args:
        working_directory: The base directory to scope file access to
        file_path: The path to the file (relative to working_directory)
    
    Returns:
        String containing file contents (truncated if > MAX_CHARS),
        or an error message string
    """
    # Get absolute paths for security check
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    
    # Security check: ensure file is within working directory
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    # Check if the path is a regular file
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    # Try to read the file
    try:
        with open(target_file, "r") as f:
            content = f.read(MAX_CHARS)
            
        # Check if we need to truncate
        with open(target_file, "r") as f:
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()
            
        if file_size > MAX_CHARS:
            content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            
        return content
    except Exception as e:
        return f"Error: {e}"


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the content of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)
