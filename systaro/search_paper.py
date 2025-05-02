import os, random, requests, json, datetime
from dotenv import load_dotenv
import os

load_dotenv()

YEARS    = range(datetime.date.today().year-2,
                 datetime.date.today().year)

def research_paper(keyword, venue):
    endpoint="https://api.semanticscholar.org/graph/v1/paper/search"
    fields = ('title', 'abstract', 'year', 'referenceCount', 'citationCount',
              'venue', 'authors')
    # venue = ('IEEE International Conference on Pervasive Computing and Communications', 'ACM SIGCHI', )
    # venue = ('Proceedings of the ACM on Interactive Mobile Wearable and Ubiquitous Technologies')
    papers = []
    for y in YEARS:
        start = f"{y}-01-01"
        end   = f"{y}-12-31"
        params = {
            'query' : keyword,
            'fields': ','.join(fields),
            'limit': 100,
            # 'venue': 'SIG CHI'
            'venue': ','.join(venue),
            'publicationDateOrYear': f"{start}:{end}"
        }

        requests_paper = requests.get(url=endpoint, params=params)
        requests_paper.raise_for_status()

        result = requests_paper.json()
        papers.extend(result.get('data', []))

        token = result.get('next') or result.get('token')
        while token:
            requests_paper = requests.get(endpoint, params={**params, 'token': token})
            requests_paper.raise_for_status()
            result = requests_paper.json()
            papers.extend(result.get('data', []))
            token = result.get('next') or result.get('token')

    if not papers:
        raise RuntimeError("条件に合う論文が見つかりませんでした。")  
    
    selected_paper = random.choice(papers)

    # 表示
    print("— 推薦論文 —")
    for f in fields:
        if f == 'authors':
            names = [a.get('name', '') for a in selected_paper.get('authors', [])]
            print(f"{f}: {names}")
        else:
            print(f"{f}: {selected_paper.get(f)}")

    return selected_paper

if __name__ == "__main__":
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    keyword =  "recognition"
    venue = ('IEEE International Conference on Pervasive Computing and Communications', 'ACM SIGCHI', )
    research_paper(endpoint, venue)