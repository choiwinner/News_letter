import feedparser
import arxiv
from datetime import datetime, timedelta
import urllib.parse

def get_google_news(keywords, days=7):
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
    
    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "source": "Google News"
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
