from ddgs import DDGS

try:
    results = DDGS().text("what does docker run -d do?", max_results=2)
    for r in results:
        print(f"Title: {r['title']}\nSnippet: {r['body']}\n")
except Exception as e:
    print(f"Error: {e}")
