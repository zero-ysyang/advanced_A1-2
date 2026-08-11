## 🗂️ API 활용 국내 여행지 추천 프로그램 개요
1. CLI 기반 Python 프로그램 실행 (입력/요청 -date "YYYY-MM-DD")
2. 입력 일자로 LLM API(Google Gemini) 연동하여 날씨/행사 정보 출력
3. 출력된 지역 기준으로 지도/장소 검색 API(Kako Local) 연동하여 맛집 검색
4. 2&3번 내용으로 LLM API 연동하여 최종 여행 리포트를 Markdown 텍스트로 생성

---

## 💻 API 키 설정 방법(.env 관리)
```
gemini_key = os.getenv("GEMINI_API_KEY")
kakao_key = os.getenv("KAKAO_REST_API_KEY")
```
---

## 🚀 실행 방법
### 1. 저장소 클론

```
git clone https://github.com/zero-ysyang/advanced_A1-2.git
cd advanced_A1-2
```
<img width="681" height="142" alt="20260811_222254" src="https://github.com/user-attachments/assets/4c07e00e-979e-4a05-b6d6-42fb8e95256b" />

### 2. 프로그램 실행 
```
python travel_planner.py --date "2026-08-XX"
```
<img width="682" height="208" alt="image" src="https://github.com/user-attachments/assets/702343a4-e3ed-4635-979a-4ca832c0ad9c" />

#### <결과 캐싱>
<img width="688" height="109" alt="캡처" src="https://github.com/user-attachments/assets/f2cb4187-f3fe-484b-bac9-021b4f700874" />

---

## 📖 결과물 확인 방법(results 폴더)
1. 원본 데이터 2026-08-XX_data.json 파일 확인
2. 최종 리포트 2026-08-XX_travel_plan.md 파일 확인

