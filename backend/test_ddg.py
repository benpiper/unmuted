from duckduckgo_search import DDGS

ddgs = DDGS()
results = ddgs.text("what does docker run -d do?", max_results=3)
for r in results:
    print(r)
