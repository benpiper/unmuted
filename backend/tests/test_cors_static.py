import ast
from pathlib import Path

def test_cors_config_static():
    # Try multiple paths to accommodate different test execution environments
    # CI runs from the 'backend' directory, while local might run from the root.
    paths_to_try = [
        Path("main.py"),
        Path("backend/main.py"),
        Path(__file__).parent.parent / "main.py"
    ]

    content = None
    selected_path = None
    for path in paths_to_try:
        if path.exists() and path.is_file():
            with open(path, "r") as f:
                content = f.read()
            selected_path = path
            break

    if content is None:
        raise FileNotFoundError(f"Could not find main.py in any of: {[str(p.absolute()) for p in paths_to_try]}")

    tree = ast.parse(content)

    found_cors = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "add_middleware":
                # Check if first arg is CORSMiddleware
                if node.args and isinstance(node.args[0], ast.Name) and node.args[0].id == "CORSMiddleware":
                    found_cors = True
                    # Check keywords
                    kwargs = {kw.arg: kw.value for kw in node.keywords}

                    # Verify allow_methods
                    if "allow_methods" in kwargs:
                        methods_node = kwargs["allow_methods"]
                        if isinstance(methods_node, ast.List):
                            methods = [elt.value for elt in methods_node.elts if isinstance(elt, ast.Constant)]
                            assert methods == ["GET", "POST", "DELETE", "OPTIONS"]

                    # Verify allow_headers
                    if "allow_headers" in kwargs:
                        headers_node = kwargs["allow_headers"]
                        if isinstance(headers_node, ast.List):
                            headers = [elt.value for elt in headers_node.elts if isinstance(elt, ast.Constant)]
                            assert headers == ["Content-Type", "Authorization"]

    assert found_cors, f"CORSMiddleware configuration not found in {selected_path}"

if __name__ == "__main__":
    try:
        test_cors_config_static()
        print("Static CORS configuration test passed!")
    except AssertionError as e:
        print(f"Static CORS configuration test failed: {e}")
        exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
