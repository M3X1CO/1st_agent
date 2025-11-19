from functions.run_python_file import run_python_file


def test():
    # Test running main.py without arguments (should print usage)
    result = run_python_file("calculator", "main.py")
    print(result)
    print("")
    
    # Test running main.py with arguments (calculator operation)
    result = run_python_file("calculator", "main.py", ["3 + 5"])
    print(result)
    print("")
    
    # Test running tests.py (unit tests)
    result = run_python_file("calculator", "tests.py")
    print(result)
    print("")
    
    # Test running file outside working directory (should error)
    result = run_python_file("calculator", "../main.py")
    print(result)
    print("")
    
    # Test running non-existent file (should error)
    result = run_python_file("calculator", "nonexistent.py")
    print(result)
    print("")
    
    # Test running non-Python file (should error)
    result = run_python_file("calculator", "lorem.txt")
    print(result)


if __name__ == "__main__":
    test()
