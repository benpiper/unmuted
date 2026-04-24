import ast

def test_cors_config_static():
    with open("backend/main.py", "r") as f:
        tree = ast.parse(f.read())

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

    assert found_cors, "CORSMiddleware configuration not found in main.py"

if __name__ == "__main__":
    try:
        test_cors_config_static()
        print("Static CORS configuration test passed!")
    except AssertionError as e:
        print(f"Static CORS configuration test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
