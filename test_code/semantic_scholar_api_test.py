import os, random, requests, json, datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


S2_KEY   = os.getenv("S2_API_KEY")
OPENAI   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# SLACK    = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))


SS_API  = os.getenv("SS_KEY")
YEARS    = range(datetime.date.today().year-2,
                 datetime.date.today().year)

def random_paper(conference: str) -> dict:
    """指定したカンファレンス名から論文をランダムで 1 本返す（API Key 不要）"""
    # ① 総件数チェック（limit=1 で軽く）
    meta = requests.get(SS_API, params={
        "query": conference,
        "limit": 1,
        "fields": "paperId"
    }).json()
    total = meta.get("total", 0)
    if total == 0:
        raise RuntimeError(f"{conference} の論文が見つからない…")

    # ② ランダム offset
    offset = random.randint(0, total - 1)

    # ③ 論文 1 本取得
    paper = requests.get(SS_API, params={
        "query": conference,
        "limit": 1,
        "offset": offset,
        "fields": "title,abstract,url,year,authors,venue"
    }).json()["data"][0]

    # ④ venue が会議名とズレることがあるので再試行ループ（最大 5 回）
    tries = 0
    while paper.get("venue", "").lower() != conference.lower() and tries < 5:
        offset = random.randint(0, total - 1)
        paper = requests.get(SS_API, params={
            "query": conference,
            "limit": 1,
            "offset": offset,
            "fields": "title,abstract,url,year,authors,venue"
        }).json()["data"][0]
        tries += 1

    return paper

def research_paper(endpoint, keyword):
    fields = ('title', 'abstract', 'year', 'referenceCount', 'citationCount',
              'venue', 'authors')
    # venue = ('IEEE International Conference on Pervasive Computing and Communications', 'ACM SIGCHI', )
    venue = ('Proceedings of the ACM on Interactive Mobile Wearable and Ubiquitous Technologies')
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



        # total = result.get('total', 0)
        # papers = result.get('data', [])
        # print(f"\n=== {y}年 ({start}～{end}) の論文: 全 {total} 件")
        # for d in papers:
        #     print('-----------------')
        #     for f in fields:
        #         if f == 'authors':
        #             # 著者リストだけ名前抽出
        #             names = [a.get('name', '') for a in d.get('authors', [])]
        #             print(f'{f}: {names}')
        #         else:
        #             print(f'{f}: {d.get(f)}')


    
    

# 確認済み
def summarize():
    client = OpenAI()
    # prompt = f"タイトル: {paper['title']}\n\n要旨: {paper['abstract']}\n\n---\nこの論文を日本語で200字以内に要約して。"
    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user", "content":"詩を英語でなんといいますか"}]
    )
    return chat.choices[0].message.content


def check_bulk():
    print()


if __name__ == "__main__":
    # paper = random_paper("CHI")        # 例：CHI
    # summary = summarize()
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    keyword =  "recognition"
    research_paper(endpoint, keyword)
    # print(summarize())
    # print(json.dumps({"paper": paper, "summary": summary}, ensure_ascii=False, indent=2))