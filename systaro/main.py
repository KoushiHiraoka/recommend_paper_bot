import os, json, sqlite3, requests, datetime, config

YEARS    = range(datetime.date.today().year-2,
                 datetime.date.today().year)

DB = sqlite3.connect("sent.db")
DB.execute("""CREATE TABLE IF NOT EXISTS sent
              (uid TEXT, doi TEXT, PRIMARY KEY(uid,doi))""")

USERS = {"alice":"D0123...", "bob":"D0456..."}  # Slack user→IM ID

def search_papers(venue):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    for y in YEARS:
        params = {
            "query": f'{venue} {y}',
            "limit": 20,
            "fields": "title,abstract,year,venue,url,externalIds",
            "api_key": config.S2_KEY,
        }
        yield from requests.get(url, params=params, timeout=30).json()["data"]

def gpt_ja(abstract):
    msg = [{"role":"system","content":"You are a helpful assistant."},
           {"role":"user",
            "content":f"以下を日本語訳→3行要約→キャッチコピー:\n{abstract}"}]
    return config.OPENAI.chat.completions.create(model="gpt-4o-mini",
                                          messages=msg).choices[0].message.content

def next_for(uid, papers):
    for p in papers:
        doi = p["externalIds"].get("DOI")
        if not doi: continue
        if not DB.execute("SELECT 1 FROM sent WHERE uid=? AND doi=?",
                          (uid,doi)).fetchone():
            return p, doi
    return None, None

def main():
    papers = list(search_papers("PerCom"))  # カンファ増やすならループ
    for uid, im in USERS.items():
        p, doi = next_for(uid, papers)
        if not p: continue
        ja = gpt_ja(p["abstract"])
        txt = f"*{p['title']}* ({p['year']})\n{ja}\n<{p['url']}|DL/DOI>"
        config.SLACK.chat_postMessage(channel=im, text=txt)
        DB.execute("INSERT OR IGNORE INTO sent VALUES (?,?,?)",
                   (uid, doi))
    DB.commit()

if __name__ == "__main__":
    main()
