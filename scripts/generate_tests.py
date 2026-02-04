import ast
import os
import sys
from google import genai

def extract_functions(file_path):
    """Parse a Python file and extract function definitions."""
    with open(file_path, 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node) or ""
            func_source = ast.get_source_segment(source, node)

            functions.append({
                'name': func_name,
                'args': args,
                'docstring': docstring,
                'source': func_source
            })

    return functions

def generate_tests_for_function(func_info):
    """Use Gemini to generate pytest tests for a function."""
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

    prompt = f"""Generate pytest tests for this Python function.

Function name: {func_info['name']}
Arguments: {', '.join(func_info['args'])}
Docstring: {func_info['docstring']}

Source code:

{func_info['source']}

Requirements:
1. Generate 3-5 meaningful test cases
2. Include edge cases (empty inputs, None values, etc.)
3. Use descriptive test function names
4. Include assertions that actually test behavior
5. Do NOT generate placeholder tests like assert True

Return ONLY the Python test code, no explanations.
"""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    return response.text
