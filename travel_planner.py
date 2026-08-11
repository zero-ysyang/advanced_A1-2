import os
import json
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. 유틸리티 함수
# ==========================================
def validate_date(date_str):
    """입력된 날짜 형식이 YYYY-MM-DD인지 검증합니다."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"잘못된 날짜 형식입니다: '{date_str}'. YYYY-MM-DD 형식으로 입력해주세요.")

def clean_json_string(text):
    """LLM 응답에서 마크다운 코드 블록을 제거합니다."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

# ==========================================
# 2. 핵심 기능 함수들
# ==========================================
def get_recommendations(client, date, errors):
    """Gemini API를 사용하여 2~3곳의 여행지 추천 JSON을 생성합니다."""
    print(f"[1/3] 1차 추천 생성 중(LLM)...")
    
    prompt = f"""
    당신은 한국 국내 여행 전문가입니다. {date}에 가기 좋은 국내 여행지 2~3곳을 추천해주세요.
    반드시 아래 JSON 형식으로만 답변하고, 다른 설명이나 마크다운(```json)은 포함하지 마세요.
    
    {{
      "recommendations": [
        {{
          "city": "도시 이름 (예: 제주, 강릉)",
          "weather": "해당 시기 일반적 날씨 요약",
          "events": ["행사/축제 후보 1", "행사/축제 후보 2", "행사/축제 후보 3"],
          "reason": "추천 근거 2~4문장"
        }}
      ]
    }}
    """
    
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
            
            json_str = clean_json_string(response.text)
            data = json.loads(json_str)
            
            if "recommendations" not in data or not isinstance(data["recommendations"], list):
                raise ValueError("필수 키 'recommendations'가 누락되었거나 배열 형식이 아닙니다.")
                
            cities = [rec["city"] for rec in data["recommendations"]]
            print(f"  - 추천된 지역: {', '.join(cities)}")
            return data
            
        except Exception as e:
            if attempt == 0:
                print(f"  - JSON 파싱 실패, 재시도 중... ({e})")
            else:
                print(f"  - LLM 응답 처리 최종 실패.")
                errors.append({"step": "llm_recommendation", "type": "JSON_PARSE_ERROR", "message": str(e)})
                return None

def search_restaurants(city, api_key, errors):
    """Kakao Local API를 사용하여 특정 지역의 맛집을 검색합니다."""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": f"{city} 맛집", "size": 5}
    
    restaurants = []
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code in [401, 403]:
            print(f"  - [{city}] 오류: 인증 실패({response.status_code}). 카카오 API 키 설정을 확인하세요.")
            errors.append({"step": "place_search", "type": "AUTH_ERROR", "message": f"HTTP {response.status_code} for {city}"})
            return restaurants
            
        response.raise_for_status()
        data = response.json()
        
        documents = data.get("documents", [])
        if not documents:
            print(f"  - [{city}] 검색 결과 0건.")
            errors.append({"step": "place_search", "type": "EMPTY_RESULT", "message": f"0 results for {city}"})
            return restaurants
            
        for doc in documents:
            restaurants.append({
                "name": doc.get("place_name", ""),
                "address": doc.get("road_address_name") or doc.get("address_name", ""),
                "category": doc.get("category_name", ""),
                "url": doc.get("place_url", "")
            })
            
        print(f"  - [{city}] 맛집 {len(restaurants)}곳 검색 완료")
        
    except Exception as e:
        print(f"  - [{city}] 맛집 검색 중 오류 발생: {e}")
        errors.append({"step": "place_search", "type": "UNKNOWN_ERROR", "message": f"{city}: {str(e)}"})
        
    return restaurants

def generate_final_report(client, date, rec_data, all_restaurants, errors):
    """Gemini API를 사용하여 지역별 최종 마크다운 리포트를 생성합니다."""
    print(f"[3/3] 최종 리포트 생성 중(LLM)...")
    
    # 데이터를 LLM이 이해하기 쉽게 텍스트로 정리
    context_text = ""
    for rec in rec_data.get("recommendations", []):
        city = rec["city"]
        context_text += f"\n### [지역: {city}]\n"
        context_text += f"- 추천 이유: {rec['reason']}\n"
        context_text += f"- 날씨: {rec['weather']}\n"
        context_text += f"- 행사: {', '.join(rec['events'])}\n"
        
        rests = all_restaurants.get(city, [])
        context_text += "- 맛집:\n"
        if not rests:
            context_text += "  데이터 없음\n"
        else:
            for i, r in enumerate(rests, 1):
                context_text += f"  {i}. {r['name']} ({r['category']}) - {r['address']} ({r['url']})\n"

    error_text = "- 발생한 오류 없음" if not errors else "\n".join([f"- [{e['step']}] {e['type']}: {e['message']}" for e in errors])

    prompt = f"""
    당신은 여행 플래너입니다. 아래 제공된 데이터를 바탕으로 {date} 국내 여행 추천 리포트를 Markdown 형식으로 작성해주세요.
    이번에는 여러 지역이 추천되었습니다. 각 지역별로 매력적인 리포트를 구성해주세요.
    
    [제공된 데이터]
    {context_text}
    
    [시스템 오류 내역]
    {error_text}
    
    [필수 포함 섹션 (Markdown 헤더 사용)]
    # {date} 국내 여행 추천 리포트
    (각 지역별로 아래 내용을 반복해서 작성해주세요)
    ## 📍 [지역명]
    ### 추천 이유 및 날씨
    ### 행사/축제
    ### 맛집 추천
    ### 1일 일정 제안 (오전/오후/저녁)
    
    (문서 맨 마지막에 한 번만 작성)
    ## ⚠️ 오류 요약(errors)
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        print("  - 리포트 생성 완료")
        return response.text
    except Exception as e:
        print(f"  - 리포트 생성 실패: {e}")
        errors.append({"step": "report_generation", "type": "LLM_ERROR", "message": str(e)})
        return "# 리포트 생성 실패\n\nLLM API 호출 중 오류가 발생했습니다."

# ==========================================
# 3. 메인 실행부
# ==========================================
def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="국내 여행지 추천 프로그램 (복수 지역 & 캐싱 지원)")
    parser.add_argument("-date", "--date", type=validate_date, required=True, help="여행 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    
    if not gemini_key or not kakao_key:
        print("🚨 [오류] API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    client = genai.Client(api_key=gemini_key)
    os.makedirs("results", exist_ok=True)
    
    json_filename = f"results/{args.date}_data.json"
    md_filename = f"results/{args.date}_travel_plan.md"
    
    # ---------------------------------------------------------
    # [캐싱 로직] 기존 파일이 있으면 API 호출 생략
    # ---------------------------------------------------------
    if os.path.exists(json_filename):
        print(f"💡 캐시 발견: {json_filename} 데이터를 재사용합니다. (API 호출 생략)")
        try:
            with open(json_filename, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            rec_data = cached_data.get("recommendation", {})
            all_restaurants = cached_data.get("restaurants", {})
            errors = cached_data.get("errors", [])
        except Exception as e:
            print(f"🚨 캐시 파일을 읽는 중 오류가 발생했습니다: {e}")
            return
    else:
        # 캐시가 없으면 정상적으로 API 호출 진행
        errors = []
        
        # 1. 1차 추천 생성 (복수 지역)
        rec_data = get_recommendations(client, args.date, errors)
        if not rec_data:
            print("🚨 추천 데이터를 가져오지 못해 프로그램을 종료합니다.")
            return
            
        # 2. 맛집 검색 (지역별 반복)
        print(f"[2/3] 맛집 검색 중(지도/장소 API)...")
        all_restaurants = {}
        for rec in rec_data.get("recommendations", []):
            city = rec["city"]
            rests = search_restaurants(city, kakao_key, errors)
            all_restaurants[city] = rests
            
        # 3. JSON 원본 저장 (캐시 생성)
        final_json_data = {
            "recommendation": rec_data,
            "restaurants": all_restaurants,
            "errors": errors
        }
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(final_json_data, f, ensure_ascii=False, indent=2)
            print(f"  - 원본 데이터 저장 완료 (캐시 생성): {json_filename}")

    # ---------------------------------------------------------
    # 4. 최종 리포트 생성 (캐시된 데이터든 새로 받은 데이터든 무조건 실행)
    # ---------------------------------------------------------
    report_md = generate_final_report(client, args.date, rec_data, all_restaurants, errors)
    
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"\n🎉 완료! {md_filename} 를 확인하세요.")

if __name__ == "__main__":
    main()