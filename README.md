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


## 🚀 실행 방법
### 1. 저장소 클론

```bash
git clone https://github.com/zero-ysyang/advanced_A1-2.git
cd advanced_A1-2
```
<img width="676" height="161" alt="20260808_183210" src="https://github.com/user-attachments/assets/897f307f-f41f-4504-a922-0a82a3f0b3ce" />


### 2. 프로그램 실행 
```bash
python travel_planner.py --date "2026-08-XX"
```

<img width="571" height="232" alt="캡처33" src="https://github.com/user-attachments/assets/f5fa6b8a-822c-470f-8df2-3db5c17e94a6" />

## 📖 결과물 확인 방법

프로그램 실행 후 메뉴 번호를 입력하여 기능을 선택합니다.

```
=== 나만의 프롬프트 관리 ===
1. 프롬프트 추가
2. 프롬프트 목록
3. 카테고리별 조회
4. 프롬프트 검색
5. 프롬프트 상세 보기
6. 즐겨찾기 관리
7. 즐겨찾기 목록
0. 종료
선택: 
```

### 1. 프롬프트 추가
```
선택: 1

=== 프롬프트 추가 ===
제목: 이메일 작성 도우미
내용: 당신은 전문 이메일 작성자입니다...

카테고리 선택:
1) 텍스트 생성
2) 이미지 생성
3) 영상 생성
4) 페르소나
5) 자동화
6) 기타
선택: 1

프롬프트가 추가되었습니다!
```
