import re
from duckduckgo_search import DDGS
import json
from play import play
from const_config import proxy

def search(q):
    if not q:
        return error_response('Please provide a query.')

    try:
        q = q[:500]
        q = escape_ddg_bangs(q)
        region ='zh-cn'
        time = 10
        max_results =  3
        response=[]
        with DDGS(proxies=proxy,timeout=time) as ddgs:
            for r in ddgs.text(q, region=region, safesearch='off', max_results=3):
                response.append(r)
        text = "\n".join(
            [f"{response[i]['body']}" for i in range(len(response)) if i < max_results]
        )
        text = text.replace("\n\n", "  ")
        play('Sound/ding.wav')
        play('Sound/searching.wav')
        print(text)
        return text

    except Exception as e:
        return error_response(f'Error searching: {e}')

def escape_ddg_bangs(q):
    q = re.sub(r'^!', r'', q)
    q = re.sub(r'\s!', r' ', q)
    return q

def error_response(message):
    response = json.dumps([{
        'body': message,
        'href': '',
        'title': ''
    }])
    return response

if __name__ == '__main__':
    print(search('近期社会新闻'))
