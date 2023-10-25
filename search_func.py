import re
from duckduckgo_search import DDGS
from newspaper import Article
import json
from play import play
from const_config import proxy

def ddg(
    keywords,
    region="wt-wt",
    safesearch="moderate",
    time=None,
    max_results=None,
    page=1,
    output=None,
    download=False,
):

    results = []
    for r in DDGS(proxies=proxy['http']).text(
        keywords=keywords, region=region, safesearch=safesearch, timelimit=time
    ):
        results.append(r)
        if (max_results and len(results) >= max_results) or (
            page and len(results) >= 20
        ):
            break
    return results


def search(q):
    if not q:
        return error_response('Please provide a query.')

    try:
        q = q[:500]
        q = escape_ddg_bangs(q)
        region =  'cn-zh'
        # safesearch =  'Off'
        time = 10
        max_results =  3
        # max_results = min(max_results, 10)

        response = ddg(q, region=region, time=time, max_results=max_results)
        # response = json.dumps(results)
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

def url_to_text(url):



    if not url:
        return error_response('Please provide a URL.')

    if '.' not in url:
        return error_response('Invalid URL.')

    try:
        title, text = extract_title_and_text_from_url(url)
    except Exception as e:
        return error_response(f'Error extracting text from URL: {e}')

    text = re.sub(r'\n{4,}', '\n\n\n', text)

    response = json.dumps([{
        'body': text,
        'href': url,
        'title': title
    }])

    return response

def error_response(message):
    response = json.dumps([{
        'body': message,
        'href': '',
        'title': ''
    }])
    return response

def extract_title_and_text_from_url(url: str):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    article = Article(url)
    article.download()
    article.parse()

if __name__ == '__main__':
    print(search('社会热点'))
