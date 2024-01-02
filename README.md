## 사용법
1. GCP 사용자 인증 정보에서 OAuth 클라이언트 ID 생성
2. 프로젝트 루트에 키 저장(ignore 되도록 키 이름은 credentials.json으로 저장해주세요.)
3. 라이브러리 다운로드
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
4. `main.py` 파일 내 FILTER 변수 값을 원하는 문자열로 변경
5. 스크립트 실행