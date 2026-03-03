from crawler import get_google_news
from summarizer import summarize_content
from mailer import format_as_html
import os
from dotenv import load_dotenv

load_dotenv()

def verify():
    print("--- Image Extraction & Layout Verification ---")
    
    # 1. 뉴스 데이터 수집 (1개만)
    print("뉴스 수집 중...")
    news_items = get_google_news("HBM", days=1)
    if not news_items:
        print("뉴스를 찾을 수 없습니다. 테스트를 종료합니다.")
        return
    
    test_item = news_items[0]
    print(f"수집된 뉴스: {test_item['title']}")
    print(f"이미지 URL: {test_item['image_url']}")
    
    # 2. 요약 생성 (이미지 정보 포함 여부 확인)
    if os.getenv("GEMINI_API_KEY"):
        print("Gemini 요약 생성 중...")
        summary = summarize_content([test_item], category="테스트 뉴스")
        print("\n--- 요약 결과 ---")
        print(summary)
        
        # 3. HTML 생성 확인
        print("\nHTML 생성 중...")
        html = format_as_html(summary, "논문 데이터 없음")
        
        with open("test_newsletter.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("검증용 HTML 파일이 생성되었습니다: test_newsletter.html")
    else:
        print("GEMINI_API_KEY가 없어 요약 및 HTML 검증을 건너뜁니다.")

if __name__ == "__main__":
    verify()
