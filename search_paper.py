import os, random, requests, json, datetime, re
from dotenv import load_dotenv

load_dotenv()

YEARS    = range(datetime.date.today().year-2,
                 datetime.date.today().year)
SS_API_KEY = os.getenv("SS_API_KEY")

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
    

# venueの指定は, で区切る．1つでも, を最後につける必要あり
def research_paper(keyword, venues):
    endpoint="https://api.semanticscholar.org/graph/v1/paper/search"
    fields = ('title', 'abstract', 'year', 'referenceCount', 'citationCount',
              'venue', 'url', 'authors')
    # venue = ('IEEE International Conference on Pervasive Computing and Communications',)
    # venue = ('Proceedings of the ACM on Interactive Mobile Wearable and Ubiquitous Technologies')
    headers    = {"x-api-key": SS_API_KEY}  
    papers = []
    total_hits = 0
    for v in venues:
        if keyword.strip() == "":
            # キーワードが空 ⇒ venue から IEEE / ACM などを抽出して使う
            dummy_query = pick_dummy_query(v)
        else:
            # キーワードあり ⇒ そのまま使う
            dummy_query = keyword 
        
        print(dummy_query)
        for y in YEARS:
            start = f"{y}-01-01"
            end   = f"{y}-12-31"
            params = {
                'query' : dummy_query,
                'fields': ','.join(fields),
                'limit': 100,
                # 'venue': 'SIG CHI'
                # 'venue': ','.join(venue),
                'venue': v, 
                'publicationDateOrYear': f"{start}:{end}"
            }

            requests_paper = requests.get(url=endpoint, params=params, headers=headers)

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
                requests_paper = requests.get(endpoint, params={**params, 'token': token}, headers=headers)
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

def check_research_paper(keyword):
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers    = {"x-api-key": SS_API_KEY} 
    fields = ('title', 'abstract', 'year', 'referenceCount', 'citationCount',
              'venue', 'url', 'authors')

    papers = []
    total_hits = 0                           # ← 追加：ヒット総数カウンタ
    # if keyword.strip() == "":
    #     # キーワードが空 ⇒ venue から IEEE / ACM などを抽出して使う
    #     dummy_query = pick_dummy_query()
    # else:
    #     # キーワードあり ⇒ そのまま使う
    #     dummy_query = keyword

    # print(dummy_query)
    # for y in YEARS:
    #     start = f"{y}-01-01"
    #     end   = f"{y}-12-31"
    params = {
        'query': keyword,
        'fields': ','.join(fields),
        'limit': 5,
        # 'venue': ','.join(venue),
        # 'corpusId': ids 
        # 'publicationDateOrYear': f"{start}:{end}"
    }

    requests_paper = requests.get(url=endpoint, params=params, headers=headers)

    # ① 年度単位でヒット総数を取得して累積
    r_dict = requests_paper.json()
    total_hits += r_dict.get('total', 0)   # ← ここで加算

    requests_paper.raise_for_status()
    result = r_dict                        # すでに JSON 化しているので再利用
    papers.extend(result.get('data', []))

    # ② ページング
    token = result.get('next') or result.get('token')
    while token:
        requests_paper = requests.get(endpoint, params={**params, 'token': token}, headers=headers)
        requests_paper.raise_for_status()
        result = requests_paper.json()
        papers.extend(result.get('data', []))
        token = result.get('next') or result.get('token')

    # ③ 何もヒットしなかった場合
    if not papers:
        raise RuntimeError("条件に合う論文が見つかりませんでした。")

    # ④ ヒット総数を一度だけ表示
    print(f"Total search result: {total_hits}")

    # ⑤ ランダムに 1 本だけ選んで表示
    selected_paper = random.choice(papers)
    print("— 推薦論文 —")
    for f in fields:
        if f == 'authors':
            names = [a.get('name', '') for a in selected_paper.get('authors', [])]
            print(f"{f}: {names}")
        else:
            print(f"{f}: {selected_paper.get(f)}")

    return selected_paper

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
    headers = {"x-api-key": SS_API_KEY}
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
   

if __name__ == "__main__":
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    keyword =  " "
    ## できるやつ
    # venue = ('Annual IEEE International Conference on Pervasive Computing and Communications',)
    # venue = ('Proceedings of the CHI Conference on Human Factors in Computing Systems',)
    venue =('International Conference on Mobile Systems, Applications, and Services',)
    # check_research_paper(keyword, venue)

    research_paper(keyword, venue)
    # check_research_paper(keyword)