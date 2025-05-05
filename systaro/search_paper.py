import os, random, requests, json, datetime, re
from dotenv import load_dotenv

load_dotenv()

YEARS    = range(datetime.date.today().year-2,
                 datetime.date.today().year)

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
def research_paper(keyword, venue):
    endpoint="https://api.semanticscholar.org/graph/v1/paper/search"
    fields = ('title', 'abstract', 'year', 'referenceCount', 'citationCount',
              'venue', 'url', 'authors')
    # venue = ('IEEE International Conference on Pervasive Computing and Communications',)
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

        ### 検索ヒット数チェック　
        r_dict = json.loads(requests_paper.text)
        total = r_dict['total']
        print(f'Total search result: {total}')
        ###

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

def check_research_paper(keyword, venues):
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = ('title', 'abstract', 'year', 'referenceCount', 'citationCount',
              'venue', 'url', 'authors')

    papers = []
    total_hits = 0                           # ← 追加：ヒット総数カウンタ
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
                'query': dummy_query,
                'fields': ','.join(fields),
                'limit': 100,
                # 'venue': ','.join(venue),
                'venue': v,
                'publicationDateOrYear': f"{start}:{end}"
            }

            requests_paper = requests.get(url=endpoint, params=params)

            # ① 年度単位でヒット総数を取得して累積
            r_dict = requests_paper.json()
            total_hits += r_dict.get('total', 0)   # ← ここで加算

            requests_paper.raise_for_status()
            result = r_dict                        # すでに JSON 化しているので再利用
            papers.extend(result.get('data', []))

            # ② ページング
            token = result.get('next') or result.get('token')
            while token:
                requests_paper = requests.get(endpoint, params={**params, 'token': token})
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

if __name__ == "__main__":
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    keyword =  " "
    venue = ('Annual IEEE International Conference on Pervasive Computing and Communications',)
    # venue =('Proceedings of the ACM on Interactive Mobile Wearable and Ubiquitous Technologies',)
    check_research_paper(keyword, venue)