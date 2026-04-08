import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# -----------------------------------------------------------------------------
# 설정 / Configuration (GitHub Secrets에서 가져옴)
# -----------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_today_menu():
    """신구대학교 홈페이지에서 오늘자 식단을 크롤링합니다."""
    url = "https://www.shingu.ac.kr/cms/FR_CON/index.do?MENU_ID=1630"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 실제 사이트 구조에 맞게 데이터를 추출해야 합니다. 
        # (임시: 사이트 구조를 파악하기 전까지는 기존 로직을 따르되, 
        #  크롤링이 실패할 경우 유의미한 메시지를 남기도록 설계합니다)
        
        # 참고: 신구대 식단표 페이지는 요일별로 테이블이 구성되어 있을 확률이 높습니다.
        # 아래는 예시 데이터입니다. 실제 연동 시 soup.find 등을 통해 추출 작업이 필요합니다.
        
        # [TODO] 사이트의 구체적인 HTML 태그를 분석하여 아래 dictionary를 채워야 합니다.
        menu_info = {
            "date": datetime.now().strftime("%Y년 %m월 %d일"),
            "student_cafeteria": {
                "breakfast": "홈페이지 참조",
                "lunch_korean": "홈페이지 참조",
                "lunch_western": "홈페이지 참조",
                "snack": "홈페이지 참조"
            },
            "staff_cafeteria": {
                "lunch": "홈페이지 참조"
            }
        }
        
        # 실제 데이터 추출 예시 (추후 사이트 구조 확인 후 상세 구현)
        # table = soup.find('table', {'class': 'menu_table'})
        # if table:
        #    ... 로직 구현 ...
            
        return menu_info
        
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return None

def format_menu_message(menu):
    """식단 데이터를 텔레그렘 메시지용 텍스트로 변환합니다."""
    if not menu:
        return "⚠️ 오늘은 식단 정보를 가져오지 못했습니다. 홈페이지를 확인해 주세요!"
        
    message = f"🏫 *신구대학교 오늘의 식단*\n📅 {menu['date']}\n\n"
    
    message += "🍱 *학생식당(서관)*\n"
    message += f"• 조식: {menu['student_cafeteria']['breakfast']}\n"
    message += f"• 중식(한식): {menu['student_cafeteria']['lunch_korean']}\n"
    message += f"• 중식(양식): {menu['student_cafeteria']['lunch_western']}\n"
    message += f"• 분식: {menu['student_cafeteria']['snack']}\n\n"
    
    message += "☕ *교직원식당*\n"
    message += f"• 중식: {menu['staff_cafeteria']['lunch']}\n\n"
    
    message += "맛있게 드세요! 😋"
    return message

def send_to_telegram(text):
    """텔레그렘으로 메시지를 전송합니다."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ 오류: TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("📋 식단 정보를 가져오는 중...")
    menu = get_today_menu()
    formatted_text = format_menu_message(menu)
    
    print("🚀 텔레그렘으로 전송 시도 중...")
    if send_to_telegram(formatted_text):
        print("✅ 성공: 오늘의 식단이 텔레그렘으로 전송되었습니다!")
    else:
        print("❌ 실패: 메시지 전송에 실패했습니다.")
