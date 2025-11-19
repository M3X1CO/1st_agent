import os
from google.genai import types


def write_file(working_directory, file_path, content):
    """
    Writes content to a file, scoped to a working directory.
    Creates the file and any necessary parent directories if they don't exist.
    
    Args:
        working_directory: The base directory to scope file access to
        file_path: The path to the file (relative to working_directory)
        content: The string content to write to the file
    
    Returns:
        String indicating success with character count,
        or an error message string
    """
    # Get absolute paths for security check
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    
    # Security check: ensure file is within working directory
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    # Try to write to the file
    try:
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(target_file)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        # Write the content to the file
        with open(target_file, "w") as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites content to a file, constrained to the working directory. Creates parent directories if needed.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)
