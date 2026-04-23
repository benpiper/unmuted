import requests

def test():
    print("starting test")
    with requests.post("http://localhost:8000/api/project/plan_stream", json={"directory_path": "/home/user/unmuted", "prompt": "", "context": ""}, stream=True) as r:
        for line in r.iter_lines():
            if line:
                print(line.decode('utf-8'))

if __name__ == '__main__':
    test()
