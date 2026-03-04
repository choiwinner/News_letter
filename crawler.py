import feedparser
import arxiv
from datetime import datetime, timedelta
import urllib.parse
from newspaper import Article, Config
from googlenewsdecoder import gnewsdecoder
import logging
import requests
import nltk

# NLTK 리소스 다운로드 (GitHub Actions 등 클린 환경 대응)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

# newspaper4k 설정 (타임아웃 등)
config = Config()
config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
config.request_timeout = 10

# newspaper4k 로그 레벨 조정 (불필요한 로그 방지)
logging.getLogger('newspaper').setLevel(logging.ERROR)

def resolve_google_news_url(url):
    """
    Google 뉴스 RSS URL을 디코딩하여 원본 기사 주소를 반환합니다.
    """
    try:
        # 1. googlenewsdecoder 시도
        result = gnewsdecoder(url)
        if result.get("status") and result.get("decoded_url"):
            return result["decoded_url"]
        
        # 2. 실패 시 requests로 리디렉션 추적 (일부 케이스 대응)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
        if response.url and "google.com" not in response.url:
            return response.url
            
        return url
    except Exception as e:
        print(f"URL 디코딩 실패: {e}")
        return url

def get_article_image(url):
    """
    newspaper4k 및 메타데이터를 사용하여 기사 URL에서 주요 이미지 URL을 추출합니다.
    """
    try:
        if "google.com" in url and "rss/articles" not in url:
            return None
            
        article = Article(url, language='ko', config=config)
        article.download()
        article.parse()
        
        # 1. newspaper4k의 기본 top_image 시도
        image = article.top_image
        
        # 2. 실패 시 OpenGraph 또는 Twitter 메타데이터 직접 확인
        if not image or "googleusercontent.com" in image or "gstatic.com" in image:
            image = article.meta_data.get('og', {}).get('image')
            if not image:
                image = article.meta_data.get('twitter', {}).get('image')
        
        # 3. 절대 경로 확인 및 구글 서버 이미지 필터링
        if image:
            if not image.startswith('http'):
                # 상대 경로인 경우 기본 URL 결합 (간단한 처리)
                from urllib.parse import urljoin
                image = urljoin(url, image)
                
            if "googleusercontent.com" in image or "gstatic.com" in image:
                return None
            
        return image
    except Exception as e:
        print(f"이미지 추출 실패 ({url}): {e}")
        return None

def get_google_news(keywords, days=7, max_results=10):
    """
    구글 뉴스 RSS를 통해 키워드 관련 뉴스를 가져옵니다.
    """
    base_url = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    # 최근 n일간의 검색 결과 필터링 (when:7d 방식)
    query = f"{keywords} when:{days}d"
    encoded_query = urllib.parse.quote(query)
    rss_url = base_url.format(query=encoded_query)
    
    feed = feedparser.parse(rss_url)
    results = []
    
    for entry in feed.entries[:max_results]:
        # 뉴스 기사의 실제 원본 URL을 찾기 위해 처리
        decoded_url = resolve_google_news_url(entry.link)
        image_url = get_article_image(decoded_url)
        
        results.append({
            "title": entry.title,
            "link": decoded_url,
            "published": entry.published,
            "source": "Google News",
            "image_url": image_url
        })
    return results

def get_arxiv_papers(keywords, max_results=5):
    """
    arXiv API를 통해 관련 논문을 가져옵니다.
    """
    search = arxiv.Search(
        query=keywords,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    results = []
    for result in search.results():
        # 최근 7일 이내 논문인지 확인 (필요시 조절)
        results.append({
            "title": result.title,
            "link": result.entry_id,
            "published": result.published.strftime("%Y-%m-%d"),
            "summary": result.summary, # LLM 요약을 위해 원문 요약 포함
            "source": "arXiv"
        })
    return results

if __name__ == "__main__":
    # 간단한 테스트
    print("--- Google News Test (HBM) ---")
    news = get_google_news("HBM 메모리 반도체", days=7)
    for n in news[:3]:
        print(f"[{n['published']}] {n['title']}\nURL: {n['link']}\n")
        
    print("\n--- arXiv Paper Test (High Bandwidth Memory) ---")
    papers = get_arxiv_papers("High Bandwidth Memory", max_results=3)
    for p in papers:
        print(f"[{p['published']}] {p['title']}\nURL: {p['link']}\n")
