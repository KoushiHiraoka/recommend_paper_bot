import os, random, requests, json, datetime, re, time
from dotenv import load_dotenv

load_dotenv()

# YEARS    = range(datetime.date.today().year-2,
#                  datetime.date.today().year)

YEARS    = range(datetime.date.today().year-1,
                 datetime.date.today().year)

SS_API_KEY = os.getenv("SS_API_KEY")

_last_call = 0.0
def rate_limited_get(url, *, params=None, headers=None):
    global _last_call
    now = time.time()
    wait = 1.0 - (now - _last_call)
    if wait > 0:                      # 前回から 1 秒経っていなければ待機
        time.sleep(wait)
    resp = requests.get(url=url, params=params, headers=headers)
    _last_call = time.time()          # 次の呼び出しまでの基準点を更新
    return resp

def get_random_paper_with_abstract(papers):
    """
    abstracts を持つ論文だけを抽出し、ランダムに 1 件返す。
    abstracts がない or 空文字のみ の論文があれば除外する。
    条件を満たす論文がなければ RuntimeError を送出。
    """
    # abstract が文字列かつ空でないものだけ残す
    papers_with_valid_abstract = [
        paper 
        for paper in papers
        if isinstance(paper.get('abstract'), str) and paper['abstract'].strip()
    ]

    if not papers_with_valid_abstract:
        raise RuntimeError("有効な abstract を持つ論文が見つかりません。")

    # フィルター済みリストからランダムに選択
    return random.choice(papers_with_valid_abstract)

def pick_dummy_query(venue_name: str) -> str:
    """
    venue_name の先頭に出てくる英語アルファベット連続語
    （IEEE / ACM / Springer など）を抽出して返す。

    例:
        "IEEE International Conference on ..." -> "IEEE"
        "ACM SIGCHI"                           -> "ACM"
        "Springer Lecture Notes..."            -> "Springer"

    もし先頭に英字が見つからなければ、検索で最も無難にヒットしやすい
    フォールバック語 'data' を返す。
    """
    # 先頭から連続する英字 (A〜Z, a〜z) を正規表現で取得
    leading_word_match = re.match(r"[A-Za-z]+", venue_name)

    if leading_word_match:
        return leading_word_match.group(0)   # "IEEE", "ACM" など
    else:
        return "data" 
    
def check_venue_name(corpus_ids):
    endpoint_base = "https://api.semanticscholar.org/graph/v1/paper/search"
    """
    corpus_ids の中からランダムに 1 件選び、詳細情報を返す。
    - corpus_ids: Semantic Scholar の Corpus ID のリスト
    """
    fields = (
        'title', 'abstract', 'year', 'referenceCount', 'citationCount',
        'venue', 'url', 'authors'
    )
    headers = {'X-API-KEY': SS_API_KEY}
    papers = []

    for cid in corpus_ids:
        url = f"{endpoint_base}/{cid}"
        params = {'fields': ','.join(fields)}
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        paper = resp.json()
        papers.append(paper)

    if not papers:
        raise RuntimeError("指定された Corpus ID に対応する論文が見つかりませんでした。")

    # ランダムに 1 件を選定
    selected = random.choice(papers)

    # 表示
    print("— 推薦論文 —")
    for f in fields:
        if f == 'authors':
            names = [a.get('name','') for a in selected.get('authors',[])]
            print(f"{f}: {names}")
        else:
            print(f"{f}: {selected.get(f)}")

    return selected

# venueの指定は, で区切る．1つでも, を最後につける必要あり
def research_paper(keyword: str, venues: dict, year_range: int):
    endpoint="https://api.semanticscholar.org/graph/v1/paper/search"
    fields = ('title', 'abstract', 'year', 'citationCount',
              'venue', 'url', 'authors')
    headers    = {"X-API-KEY": SS_API_KEY}  
    papers = []

    total_hits = 0

    selected_venue = random.choice(venues)
    print(selected_venue)
    for y in range(year_range): 
        if keyword.strip() == "":
            # キーワードが空 ⇒ venue から IEEE / ACM などを抽出して使う
            dummy_query = pick_dummy_query(selected_venue)
        else:
            # キーワードあり ⇒ そのまま使う
            dummy_query = keyword 
        
        print(dummy_query)
        # start = f"{datetime.date.today().year-2}-01-01"
        start = f'{datetime.date.today().year-y}-01-01'
        end   = f"{datetime.date.today().year-y}-12-31"
        params = {
            'query' : dummy_query,
            'fields': ','.join(fields),
            'limit': 100,
            'venue': selected_venue, 
            'publicationDateOrYear': f"{start}:{end}"
        }

        requests_paper = rate_limited_get(url=endpoint, params=params, headers=headers)

        # API Keyが通ってるかチェック
        print("SS_API_KEY:", os.getenv("SS_API_KEY")[:4], "****")
        print("Request headers:", requests_paper.request.headers)
        print("Status:", requests_paper.status_code)

        ### 検索ヒット数チェック　
        # r_dict = json.loads(requests_paper.text)
        # total = r_dict['total']
        # print(f'Total search result: {total}')
        ###

        r_dict = requests_paper.json()
        total_hits += r_dict.get('total', 0)

        requests_paper.raise_for_status()
        result = r_dict
        papers.extend(result.get('data', []))

        token = result.get('next') or result.get('token')
        while token:
            requests_paper = rate_limited_get(endpoint, params={**params, 'token': token}, headers=headers)
            requests_paper.raise_for_status()
            result = requests_paper.json()
            papers.extend(result.get('data', []))
            token = result.get('next') or result.get('token')

    if not papers:
        raise RuntimeError("条件に合う論文が見つかりませんでした。")  
    
    print(f"Total search result: {total_hits}")

    # selected_paper = random.choice(papers)
    selected_paper = get_random_paper_with_abstract(papers)

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
    keyword =  " "
    venue = ('Annual IEEE International Conference on Pervasive Computing and Communications','CHI')
    year_range = 3

    research_paper(keyword, venue, year_range)
