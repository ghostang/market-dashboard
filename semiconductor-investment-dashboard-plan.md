# Semiconductor Investment Dashboard Plan

작성일: 2026-06-27

> 최신 운영 기준: 이 문서는 static HTML + GitHub Pages + 실제 소스 generated JSON 방식을 기준으로 한다. 아래의 초기 탐색 섹션에서 Streamlit/DuckDB/SQLite 후보가 언급되더라도, MVP 구현·운영 기준은 17~18장의 정적 Pages/No-mock/실제 소스 연결 규칙이 우선한다.

## 1. 목적

한국 코스피, 반도체, 메모리 중심 투자 판단을 돕는 개인용 대시보드를 만든다. 목표는 종목 추천이나 매매 자동화가 아니라, 보유 논리와 시장 사이클을 반복적으로 검증하는 것이다.

핵심 질문:

- 한국 반도체/메모리 투자 논리가 아직 유효한가?
- 주가 상승이 수출, 메모리 가격, 실적, 외국인 수급으로 확인되는가?
- 한국 종목과 TSMC, Broadcom, Micron 같은 글로벌 피어 사이에 괴리가 생겼는가?
- 내 포트폴리오가 특정 리스크에 과도하게 쏠려 있는가?

## 2. 범위

### 포함

- KOSPI, KOSPI200, 한국 반도체 주요 종목, 관련 ETF 가격과 수익률
- 외국인/기관/개인 수급, 거래대금, 공매도 등 시장 온도 지표
- 한국 반도체/메모리 수출 지표
- DRAM, NAND, HBM 사이클 지표 또는 프록시
- Samsung Electronics, SK hynix, TSMC, Broadcom, Micron 실적/가이던스 추적
- 환율, 금리, SOX 등 매크로/글로벌 비교 지표
- 개인 포트폴리오 비중, 손익, 집중도, 리스크 신호
- 데이터 출처, 갱신일, 품질 상태, 수집 실패 여부 표시

### 제외

- 자동 매매
- 특정 종목 매수/매도 추천
- 초단타용 실시간 호가/틱 데이터
- 출처가 불명확한 커뮤니티/블로그 기반 수치
- 유료 데이터 무단 크롤링

## 3. 핵심 설계 원칙

1. 공식/공공/IR 소스를 우선한다.
2. 무료로 정확히 얻기 어려운 데이터는 프록시와 유료 옵션을 명확히 구분한다.
3. 모든 숫자는 source, as_of_date, fetched_at, refresh_status를 가진다.
4. 대시보드 첫 화면은 5분 안에 현재 투자 논리를 점검할 수 있어야 한다.
5. 데이터 수집 실패는 조용히 숨기지 않고 화면에 표시한다.
6. 수동 입력이 필요한 데이터는 자동 데이터와 분리한다.

## 4. 대시보드 화면 구성

### 4.1 시장 온도

목적: 한국 반도체 주식이 시장 대비 얼마나 강한지, 수급이 따라오는지 확인한다.

표시 항목:

- KOSPI, KOSPI200, SOX, USD/KRW
- 삼성전자, SK하이닉스, 주요 반도체 ETF
- TSMC, Broadcom, Micron
- 1일, 1주, 1개월, 3개월, YTD 수익률
- 20일/60일 이동평균 대비 위치
- 거래대금 변화
- 외국인/기관/개인 순매수
- 공매도 비중

주요 판단:

- 주가 강세가 지수 대비 초과수익인지
- 외국인이 계속 매수하는지
- 거래대금 없이 가격만 오르는지
- 한국과 미국/대만 피어 간 괴리가 커지는지

### 4.2 메모리 사이클

목적: 메모리 업황이 실제로 개선 중인지 확인한다.

표시 항목:

- 한국 반도체 수출 YoY/MoM
- DRAM/NAND 수출 또는 가격 프록시
- 글로벌 반도체 매출 성장률
- Micron 매출, gross margin, inventory commentary
- SK hynix DRAM/NAND/HBM 관련 IR 코멘트
- Samsung DS/Memory 실적 코멘트
- TSMC 월매출 추세

주요 판단:

- 주가가 실물 수출보다 먼저 과하게 달렸는지
- 메모리 가격 또는 프록시가 꺾이고 있는지
- HBM 강세가 범용 DRAM/NAND로 확산되는지

### 4.3 글로벌 피어

목적: 한국 반도체 투자 논리를 글로벌 AI/반도체 체인과 대조한다.

표시 항목:

- TSMC 월매출 YoY/MoM
- Broadcom AI/semiconductor revenue, guidance
- Micron DRAM/NAND revenue, margin, inventory
- SOX index
- peer basket 수익률
- 한국 memory basket 대비 spread

주요 판단:

- 한국 메모리 주식이 글로벌 피어 대비 과열인지
- AI 인프라 수요가 계속 강한지
- Micron 실적과 SK hynix/Samsung 주가 방향이 충돌하는지

### 4.4 포트폴리오 리스크

목적: 내 계좌가 어떤 리스크에 노출되어 있는지 확인한다.

표시 항목:

- 종목별 평가금액, 손익률, 비중
- 한국 비중, 미국/대만 비중, 달러 노출
- 메모리 비중, 파운드리 비중, AI 인프라 비중
- 단일 종목 집중도
- 고점 대비 하락률
- 손절/리밸런싱 기준 메모

주요 판단:

- 한국 메모리에 너무 몰려 있는지
- 환율 변화에 취약한지
- 특정 종목이 계좌 전체를 지배하는지

### 4.5 이벤트 캘린더

목적: 실적, 수출, 월매출, 금리 이벤트 전후 변동성을 관리한다.

표시 항목:

- 한국 월간 수출 발표
- TSMC 월매출 발표
- Samsung/SK hynix/Micron/Broadcom 실적 발표
- FOMC, 한국은행 금통위
- 주요 배당락/실적 컨퍼런스콜

주요 판단:

- 큰 이벤트 직전에 포지션이 과도한지
- 실적 발표 후 투자 논리를 업데이트했는지

## 5. 데이터 소스 매트릭스

| 영역 | 데이터 | 1순위 소스 | 접근 방식 | 갱신 주기 | 대안/프록시 | 주의점 |
|---|---|---|---|---|---|---|
| 한국 시세 | KOSPI, KOSPI200, 개별 종목 OHLCV | KRX Open API / KRX 정보데이터시스템 | API 또는 CSV 다운로드 | 일 1회, 장마감 후 | pykrx 등 KRX 기반 라이브러리 | 라이브러리는 공식 API가 아니므로 source는 KRX로 표기하되 수집기는 별도 표기 |
| 한국 수급 | 외국인/기관/개인 순매수 | KRX 정보데이터시스템 | API/CSV | 일 1회 | 증권사 HTS CSV 수동 업로드 | 시장/종목 단위 grain을 분리 |
| 공매도 | 공매도 거래대금/비중 | KRX 정보데이터시스템 | API/CSV | 일 1회 | 없음 | 공매도 재개/제도 변경 시 정의 업데이트 필요 |
| 한국 공시 | 사업보고서, 분기보고서, 주요사항 | OPENDART | API | 공시 발생 시/일 1회 | 기업 IR 페이지 | DART 표준계정과 IR 사업부 수치가 다를 수 있음 |
| 한국 실적 | 삼성전자, SK hynix 사업부 실적 | 기업 IR, DART | IR PDF/HTML + DART API | 분기 | 뉴스룸 요약 | 사업부별 수치는 DART보다 IR 자료가 더 설명력이 높을 수 있음 |
| 수출 | 반도체/메모리 수출 YoY/MoM | MOTIR 수출입 동향, 관세청/공공데이터 | 보도자료 + 원자료 API/CSV | 월 1회 | KITA 통계 | 품목코드 기준이 HS/MTI/보도자료마다 다를 수 있음 |
| 글로벌 반도체 | 전세계 반도체 매출 | SIA, WSTS | 월간 보도자료/데이터 | 월/분기 | 없음 | 상세 WSTS 데이터는 접근 제한 가능 |
| 메모리 가격 | DRAM/NAND spot/contract | TrendForce/DRAMeXchange 등 | 유료 API/리포트 | 주/월 | 수출 단가, Micron margin, SK hynix ASP 코멘트 | 무료 대체값은 가격 자체가 아니라 프록시로 표시 |
| TSMC | 월매출 | TSMC Investor Relations | HTML/CSV 수집 | 월 1회 | SEC/ADR 관련 자료 | TWD 기준. 환산 여부 명시 |
| Broadcom | 매출, AI 관련 코멘트, 가이던스 | Broadcom IR, SEC EDGAR | IR press release + SEC companyfacts | 분기 | earnings transcript provider | AI revenue 표현은 회사 발표 기준 그대로 저장 |
| Micron | DRAM/NAND 매출, margin, 재고 | Micron IR, SEC EDGAR | IR press release + SEC companyfacts | 분기 | transcript provider | fiscal quarter 기준이 calendar quarter와 다름 |
| 미국 시세 | TSM, AVGO, MU, SOX | 유료 시세 API 우선 | API | 일 1회 | Alpha Vantage, Stooq 등 무료/지연 데이터 | 무료 데이터는 라이선스/지연/정확도 한계 표시 |
| 환율 | USD/KRW | BOK ECOS | API | 일 1회 | FRED/시장데이터 API | 기준시각과 고시환율 정의 확인 |
| 금리 | 미국 10년물, 한국 기준금리 | FRED, BOK ECOS | API | 일 1회/이벤트 | Treasury API | 휴일 결측 처리 필요 |
| 포트폴리오 | 보유수량, 평균단가, 평가금액 | 사용자의 증권사 CSV/수기 입력 | CSV 업로드 | 사용자가 갱신할 때 | 수동 입력 폼 | 계좌 원본 파일은 로컬 보관, 민감정보 최소화 |

## 6. 데이터 모델 초안

### 6.1 공통 컬럼

모든 fact 테이블은 가능한 한 아래 컬럼을 가진다.

- source_name
- source_url
- source_type: official, public_api, company_ir, paid_vendor, manual, proxy
- as_of_date
- fetched_at
- refresh_status: ok, stale, failed, manual_required
- quality_note

### 6.2 테이블

#### market_daily

용도: 가격, 거래량, 수익률 계산

컬럼:

- trade_date
- market
- ticker
- name
- currency
- open
- high
- low
- close
- volume
- trading_value
- source_name
- fetched_at

#### flow_daily

용도: 외국인/기관/개인 수급

컬럼:

- trade_date
- market
- ticker nullable
- investor_type
- net_buy_value
- net_buy_volume
- source_name
- fetched_at

#### macro_daily

용도: 환율/금리/매크로 비교

컬럼:

- date
- indicator
- value
- unit
- source_name
- fetched_at

#### exports_monthly

용도: 한국 반도체 수출 사이클 확인

컬럼:

- month
- category
- value_usd
- yoy_pct
- mom_pct
- source_code_system
- source_name
- quality_note

#### memory_cycle_monthly

용도: 메모리 가격 또는 프록시 추적

컬럼:

- month
- product
- metric
- value
- unit
- is_proxy
- source_name
- quality_note

#### company_quarterly

용도: 기업별 실적/마진/가이던스

컬럼:

- fiscal_period
- calendar_period
- company
- segment
- metric
- value
- unit
- source_name
- source_url
- quality_note

#### event_calendar

용도: 주요 발표 일정 관리

컬럼:

- event_date
- event_type
- company_or_source
- title
- expected_time
- source_url
- status

#### portfolio_positions

용도: 개인 보유 현황

컬럼:

- snapshot_date
- account_label
- ticker
- name
- quantity
- avg_cost
- market_price
- market_value
- currency
- asset_theme
- country
- manual_note

#### signals_daily

용도: 신호등 결과 저장

컬럼:

- date
- signal_group
- signal_name
- status: green, yellow, red, unavailable
- score
- reason
- source_dependencies

## 7. 수집 전략

### 7.1 MVP 단계

먼저 자동화하기 쉬운 데이터부터 채운다.

1. 한국/미국/대만 주요 가격 데이터
2. KOSPI, SOX, USD/KRW, 미국 10년물
3. 포트폴리오 CSV 수동 업로드
4. TSMC 월매출 수동/반자동 수집
5. Samsung, SK hynix, Micron, Broadcom 실적 발표 링크 수동 등록

이 단계의 목표는 화면 구조와 계산 로직을 먼저 검증하는 것이다.

### 7.2 공식 소스 자동화 단계

1. KRX Open API 또는 KRX CSV 수집기를 붙인다.
2. OPENDART API로 한국 공시/재무제표를 수집한다.
3. BOK ECOS와 FRED API로 환율/금리를 수집한다.
4. TSMC IR 월매출 테이블을 자동 수집한다.
5. SEC EDGAR companyfacts로 Broadcom/Micron 재무 항목을 검증한다.

### 7.3 사이클 데이터 고도화 단계

1. MOTIR 월간 수출 보도자료 숫자를 구조화한다.
2. 관세청/공공데이터 원자료와 보도자료 수치를 대조한다.
3. SIA/WSTS 글로벌 반도체 매출을 추가한다.
4. 유료 메모리 가격 데이터 사용 여부를 결정한다.
5. 유료 데이터가 없으면 memory_cycle_monthly에 프록시 플래그를 명확히 둔다.

## 8. 지표 계산 규칙

### 8.1 수익률

- 1D: 전 거래일 종가 대비
- 1W: 5거래일 전 대비
- 1M: 21거래일 전 대비
- 3M: 63거래일 전 대비
- YTD: 해당 연도 첫 거래일 대비

### 8.2 이동평균 위치

- close / moving_average_n - 1
- 기본 n: 20, 60, 120

### 8.3 수급 강도

- 외국인 순매수 금액 / 최근 20거래일 평균 거래대금
- 기관 순매수 금액 / 최근 20거래일 평균 거래대금

### 8.4 사이클 점수

초기 버전은 단순 규칙 기반으로 시작한다.

- 수출 YoY 증가: +1
- 수출 MoM 증가: +1
- TSMC 월매출 YoY 증가: +1
- Micron gross margin 개선: +1
- SK hynix/Samsung IR에서 HBM/DRAM 긍정 코멘트 확인: +1
- 메모리 가격 또는 프록시 하락: -1
- 외국인 순매도 지속: -1

점수 해석:

- 4 이상: green
- 1~3: yellow
- 0 이하: red
- 핵심 데이터 2개 이상 누락: unavailable

### 8.5 포트폴리오 집중도

- 단일 종목 비중
- 국가별 비중
- 메모리 테마 비중
- 원화/달러 노출
- 상위 3개 종목 합산 비중

## 9. 데이터 품질 검증

### 9.1 수집 검증

- 필수 데이터가 최근 예정 갱신일 안에 들어왔는지 확인한다.
- 같은 source_name에서 중복 row가 생기지 않는지 확인한다.
- 영업일/휴일 결측을 구분한다.
- 통화 단위를 저장하고 변환 여부를 명시한다.

### 9.2 수치 검증

- KRX 종가와 대시보드 종가가 일치하는지 샘플 검증한다.
- 수익률 계산은 원천 종가에서 재계산한다.
- 월간 수출 YoY/MoM은 원자료 값으로 재계산하고 보도자료와 비교한다.
- TSMC 월매출은 TWD 원자료와 환산값을 분리한다.
- fiscal quarter와 calendar quarter를 혼동하지 않는다.

### 9.3 화면 검증

- 모든 카드에 최근 갱신일이 보이는지 확인한다.
- stale/failed/manual_required 상태가 화면에 드러나는지 확인한다.
- 프록시 데이터는 실제 가격 데이터처럼 표시하지 않는다.
- 포트폴리오 원본 CSV에 민감정보가 있으면 저장하지 않는다.

## 10. 구현 단계

### Phase 0: 계획 확정

산출물:

- 이 계획 문서
- MVP 범위 결정
- 필요한 API 키 목록
- 포트폴리오 CSV 형식 결정

검증:

- 각 화면의 핵심 질문이 명확한지 확인
- 각 지표의 소스와 대안이 정의됐는지 확인

### Phase 1: 로컬 MVP

산출물:

- 로컬 데이터 폴더
- seed config
- market_daily, macro_daily, portfolio_positions
- 기본 대시보드 첫 화면

검증:

- 샘플 종목 가격과 수익률 계산 확인
- 포트폴리오 비중 합계 100% 확인
- 데이터 갱신일 표시 확인

### Phase 2: 공식 데이터 자동 수집

산출물:

- KRX 수집기
- BOK/FRED 수집기
- OPENDART 기본 수집기
- TSMC 월매출 수집기

검증:

- 재실행해도 중복 데이터가 생기지 않음
- API 실패 시 refresh_status가 failed로 표시됨
- 장마감 전/후 데이터 기준이 명확함

### Phase 3: 사이클/실적 확장

산출물:

- exports_monthly
- memory_cycle_monthly
- company_quarterly
- event_calendar

검증:

- 월간 수출 숫자가 보도자료와 재계산값 기준으로 설명 가능
- Micron/Broadcom fiscal period가 올바르게 매핑됨
- 프록시와 실데이터가 명확히 구분됨

### Phase 4: 신호등/알림

산출물:

- signals_daily
- 신호등 카드
- 이벤트 전후 경고
- 데이터 stale 경고

검증:

- 신호 변경 이유가 reason 컬럼에 남음
- unavailable이 red처럼 오해되지 않음
- 알림이 투자 권유 문구로 보이지 않음

## 11. 기술 선택 후보

### 보수적 MVP

- Python
- DuckDB 또는 SQLite
- CSV/Parquet 저장
- Streamlit 또는 정적 HTML

장점:

- 빠르게 만들 수 있음
- 로컬에서 민감한 포트폴리오 데이터를 다루기 쉬움
- 데이터 모델을 검증하기 좋음

단점:

- 장기 운영 UI는 다소 투박할 수 있음

### 확장형

- Python ETL
- DuckDB/SQLite
- React/Vite frontend
- scheduled job

장점:

- 화면 품질과 인터랙션을 더 좋게 만들 수 있음
- 나중에 자동 알림/배포 확장 가능

단점:

- MVP 속도가 느려질 수 있음

초기 권장안:

- 먼저 Python + DuckDB + Streamlit 또는 HTML로 MVP를 만든다.
- 데이터 모델과 신호 규칙이 안정되면 React/Vite로 옮긴다.

## 12. API 키와 접근 권한

필요 가능성이 높은 것:

- KRX Open API 또는 KRX 데이터 접근 방식
- OPENDART API key
- BOK ECOS API key
- FRED API key
- 미국 시세 API key
- 유료 메모리 가격 데이터 접근권, 선택 사항

민감정보 처리:

- API 키는 .env에 둔다.
- 포트폴리오 원본 CSV는 git에 넣지 않는다.
- 계좌번호, 주문번호, 개인정보 컬럼은 import 단계에서 제거한다.

## 13. 리스크와 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| KRX 자동 수집 제한 | 한국 가격/수급 자동화 지연 | MVP는 수동 CSV 허용, 이후 API 안정화 |
| 메모리 가격 데이터 유료 | 핵심 사이클 지표 빈틈 | 프록시 표시 또는 유료 구독 결정 |
| IR PDF 구조 변경 | 자동 파싱 실패 | 핵심 실적은 수동 검증 필드 유지 |
| 미국 무료 시세 지연/라이선스 | 피어 비교 정확도 제한 | 유료 API 또는 장마감 지연 데이터로 명시 |
| fiscal/calendar period 혼동 | 실적 비교 오류 | fiscal_period와 calendar_period를 분리 저장 |
| 포트폴리오 민감정보 노출 | 개인정보 리스크 | 로컬 저장, 원본 CSV 미보관, 컬럼 whitelist |
| 신호등 과신 | 기계적 매매 오해 | reason과 source_dependencies를 함께 표시 |

## 14. MVP에서 반드시 답해야 할 질문

1. 오늘 한국 반도체가 KOSPI와 글로벌 피어 대비 강한가?
2. 외국인 수급이 주가 상승을 확인해주는가?
3. 한국 반도체 수출과 TSMC/Micron 데이터가 같은 방향인가?
4. 내 포트폴리오가 메모리/한국/단일 종목에 얼마나 쏠려 있는가?
5. 다음 주요 이벤트 전까지 확인해야 할 리스크는 무엇인가?

## 15. 구현 전 체크리스트

- [ ] MVP 화면을 Streamlit, HTML, React 중 무엇으로 만들지 결정
- [ ] 포트폴리오 CSV 샘플 형식 결정
- [ ] API 키가 필요한 소스와 수동으로 시작할 소스 구분
- [ ] 무료 미국 시세 소스의 라이선스/지연 조건 확인
- [ ] 메모리 가격을 유료 데이터로 쓸지 프록시로 시작할지 결정
- [ ] 데이터 저장 위치와 민감정보 제외 규칙 확정
- [ ] 첫 구현 범위를 Phase 1로 제한

## 16. 첫 구현 권장 범위

가장 작은 유용한 버전:

- KOSPI, KOSPI200, 삼성전자, SK하이닉스, TSMC, Broadcom, Micron, SOX 가격/수익률
- USD/KRW, 미국 10년물
- 포트폴리오 CSV 업로드
- TSMC 월매출 수동 입력 또는 반자동 수집
- 한국 반도체 수출 월간 수동 입력
- 간단한 green/yellow/red 신호등

이 범위만으로도 투자 판단에 필요한 첫 계기판은 만들 수 있다. 이후 자동화와 세부 사이클 데이터는 단계적으로 붙인다.

## 17. 2026-06-27 수정: 정적 HTML/GitHub Pages 운영 기준

사용자 목표를 `static HTML + GitHub Pages`로 확정한다. Streamlit, 서버 DB, 브라우저 내 API key 호출은 MVP 운영 경로에서 제외한다.

### 17.1 운영 아키텍처

```text
GitHub Actions 또는 로컬 Python 수집기
  -> 실제 외부 소스 호출
  -> public/data/dashboard.json 생성
  -> public/index.html, public/app.js, public/styles.css가 정적 JSON만 읽음
  -> GitHub Pages에서 정적 파일 배포
```

규칙:

1. GitHub Pages 런타임에는 서버가 없다고 가정한다.
2. API key가 필요한 소스는 브라우저에서 직접 호출하지 않는다.
3. 운영 산출물은 HTML/CSS/JS/JSON만 배포한다.
4. DuckDB/SQLite는 빌드 타임 내부 캐시로만 사용할 수 있고 Pages 런타임 DB로 쓰지 않는다.
5. `public/data/dashboard.json`의 `mock_data`는 반드시 `false`여야 한다.

### 17.2 UI 방향성

첨부된 목표 이미지를 기준으로 한다.

- 어두운 네이비 좌측 사이드바 + 밝은 본문
- 상단 헤더: 제목, 실제 소스 배지, 마지막 업데이트, 기간 선택
- 1행: KOSPI, 삼성전자, SK하이닉스, TSMC, Broadcom, Micron 핵심 카드
- 각 카드: 현재값, 등락률, 미니 sparkline, as-of/status
- 중앙: 주요 지수 비교 라인 차트
- 우측/하단: 데이터 소스 상태, 투자 신호, SEC 실적 fact, 포트폴리오 리스크
- 텍스트보다 표/카드/차트 중심으로 5분 안에 온도 확인
- `예시 데이터` 배지가 아니라 `실제 소스`, `manual_required`, `failed`, `unavailable` 상태를 명확히 표시

### 17.3 No-mock 정책

운영 build는 mock/sample/random 데이터를 포함하지 않는다.

- 실제 소스 호출 실패 시 fake 값을 넣지 않는다.
- 실패한 지표는 `refresh_status=failed`로 렌더링한다.
- 아직 연결하지 못한 지표는 `manual_required` 또는 `unavailable`로 렌더링한다.
- 유료 데이터가 필요한 DRAM/NAND spot/contract 가격은 임의 숫자로 채우지 않는다.
- CI는 `mock_data=false`와 `source_type != mock`을 검사한다.

## 18. 현재 실제 연결된 소스와 미연결 소스

### 18.1 현재 연결 완료

| 영역 | 항목 | 연결 방식 | 상태 | 비고 |
|---|---|---|---|---|
| 한국 지수 | KOSPI | Naver Stock chart JSON | connected | KRX 공식 API 전 단계의 실제 시장 데이터 provider |
| 한국 종목 | 삼성전자 005930, SK하이닉스 000660 | Naver Stock domestic chart JSON | connected | OHLCV 시계열 수집 |
| 글로벌 가격 | TSMC 2330.TW, Broadcom AVGO, Micron MU, SOX, USD/KRW, 미국 10년물 | Yahoo Finance chart JSON | connected | 무료/비공식 provider이므로 quality_note에 한계 표시 |
| 글로벌 실적 fact | Micron, Broadcom revenue/gross profit/net income | SEC EDGAR companyfacts API | connected | 공식 public API. segment/AI revenue 코멘트는 별도 IR 파싱 필요 |
| 정적 표시 | 카드, watchlist, 비교 차트, source status, signal table | `public/index.html` + `public/app.js` | connected | `public/data/dashboard.json`만 읽음 |

### 18.2 아직 가짜로 채우지 않는 항목

| 영역 | 상태 | 이유 | 다음 연결 방식 |
|---|---|---|---|
| DRAM/NAND/HBM 가격 | `manual_required` | 안정적인 무료 공개 API가 없고 유료 데이터 성격 | TrendForce/DRAMeXchange 유료 또는 사용자가 업로드한 실제 CSV |
| 한국 수출 YoY/MoM | `manual_required` 예정 | MOTIR/KCS/data.go.kr 원자료 endpoint/API key와 품목코드 확정 필요 | 월간 CSV/공공 API 연결 후 `exports_monthly` 생성 |
| OPENDART 한국 공시/재무 | key 필요 | API key 없이는 운영 자동화 불가 | GitHub Actions Secret `OPENDART_API_KEY` 추가 후 연결 |
| BOK ECOS/FRED macro | key 또는 provider 안정성 필요 | 직접 확인에서 FRED CSV timeout이 있었음 | key 기반 API 또는 재시도/cache 추가 |
| 개인 포트폴리오 | `manual_required` | 공개 Pages에 보유내역 JSON 배포 위험 | 브라우저 로컬 CSV import 우선 |

### 18.3 구현 산출물

- `scripts/fetch_dashboard_data.py`: 실제 소스에서 정적 JSON 생성
- `tests/test_fetch_dashboard_data.py`: provider payload normalize, no-mock, SEC fact 추출 검증
- `public/data/dashboard.json`: 현재 실제 소스 snapshot
- `public/index.html`, `public/styles.css`, `public/app.js`: GitHub Pages용 정적 대시보드
- `.github/workflows/update-dashboard-data.yml`: 평일 스케줄/수동 실행으로 실제 데이터 갱신, mock guard 실행

### 18.4 운영 검증 기준

1. `python tests/test_fetch_dashboard_data.py -v` 통과
2. `python scripts/fetch_dashboard_data.py --out public/data/dashboard.json` 실행 시 `mock_data=False`
3. market cards가 하나 이상 `refresh_status=ok`
4. GitHub Actions mock guard에서 `source_type=mock` 행이 없어야 함
5. 브라우저 렌더링에서 source status에 manual/failed/unavailable이 숨겨지지 않아야 함

## 19. 추가 요구사항: AI 칩 밸류체인과 Favorite 소스

### 19.1 목표

기존 메모리 중심 시야를 AI 칩 전체 공급망으로 확장한다. 첫 화면에서 사용자가 아래 질문을 한눈에 확인할 수 있어야 한다.

1. AI 칩 밸류체인 중 어느 구간이 강한가?
2. 설계, 파운드리, 메모리, 기판/소재·부품 중 어느 테마가 주가/실적/뉴스 모멘텀이 좋은가?
3. 대표 기업의 실적, 점유율 또는 점유율 proxy, 주요 뉴스가 같은 방향인가?
4. 내가 중요하게 보는 한국은행, 슈카월드, 토스증권 소스에서 반도체/AI/매크로 관련 새 내용이 나왔는가?

이 확장은 투자 추천이 아니라, AI 반도체 투자 논리를 점검하는 관찰 패널이다.

### 19.2 AI 칩 밸류체인 테마 분류

| 테마 | 의미 | 대표 기업 초기 universe | 핵심 확인 지표 | 주의점 |
|---|---|---|---|---|
| 팹리스/설계 | GPU, AI accelerator, ASIC, 네트워크 칩 설계 | NVIDIA, AMD, Broadcom, Qualcomm, Marvell, Arm | 주가 모멘텀, 매출/마진, AI/data center revenue, 가이던스, 주요 제품 뉴스 | AI 매출 비중은 기업별 정의가 다르므로 원문 표현 그대로 저장 |
| 파운드리/생산 | 첨단 공정 제조와 패키징 capacity | TSMC, Samsung Electronics/Foundry, Intel Foundry, GlobalFoundries, UMC | 월매출, capex, gross margin, advanced node 수요, 고객/공정 뉴스 | TSMC 월매출은 연결 가능하되, 시장 점유율은 TrendForce/Omdia 등 외부 리포트 의존 가능 |
| 메모리/HBM/DRAM/NAND | HBM, DRAM, NAND, enterprise SSD | SK hynix, Samsung Electronics, Micron | HBM 코멘트, DRAM/NAND 가격 또는 proxy, gross margin, inventory, 수출, 고객 인증 뉴스 | DRAM/NAND/HBM 가격은 유료/수동 실제 소스 없으면 임의 숫자 금지 |
| 기판/소재·부품 | FC-BGA, ABF substrate, MLCC, 패키징/공정 소재·부품 | Samsung Electro-Mechanics, Ibiden, Unimicron, Shinko, Shin-Etsu, SUMCO, Soulbrain, Wonik Materials 등 | FC-BGA/MLCC 수요, capex, 수주/증설, 관련 매출, 주가 모멘텀 | 일부 기업은 segment 데이터가 부족하므로 IR/공시/뉴스 기반 manual_real부터 시작 |

초기 화면에서는 각 테마별 대표 3~5개만 보여주고, 전체 universe는 별도 config에서 관리한다.

### 19.3 화면 구성: AI 칩 밸류체인 탭

새 탭: `AI 칩 체인`

구성:

1. **밸류체인 온도맵**
   - 4개 테마 카드: 팹리스, 파운드리, 메모리, 기판/소재·부품
   - 각 카드 표시: 1D/1M/YTD 테마 바스켓 수익률, 대표 기업 1~2개, source status
   - 색상: green/yellow/red/unavailable. unavailable은 red처럼 보이지 않게 회색/점선 처리

2. **대표 기업 현황 표**
   - 컬럼: 테마, 기업, ticker, 현재가, 1M, YTD, 최근 실적 fact, 점유율/점유율 proxy, 최근 뉴스, source status
   - 주가/실적은 가능한 자동 real source
   - 점유율은 `official/company_ir/paid_vendor/manual_real/proxy_real` 중 하나로 표시

3. **점유율/현황 패널**
   - 팹리스: AI/data center revenue share 또는 기업별 AI 매출 proxy
   - 파운드리: foundry revenue share, advanced node exposure
   - 메모리: HBM/DRAM/NAND share 또는 proxy
   - 기판/소재: ABF/FC-BGA/MLCC exposure proxy
   - 신뢰 가능한 수치가 없으면 `manual_required`로 표시하고 숫자를 만들지 않는다.

4. **주요 뉴스/이벤트 레일**
   - 기업 IR/news, SEC filings, BOK/favorite sources, 사용자가 지정한 URL에서 관련 키워드 필터링
   - 키워드 예: AI chip, GPU, HBM, DRAM, NAND, foundry, TSMC, NVIDIA, SK hynix, Samsung, Micron, FC-BGA, ABF, MLCC, 반도체, 인공지능, 수출, 금리

### 19.4 Favorite 소스 패널

새 탭 또는 우측 고정 패널: `Favorite 소스`

표시 목적:

- 숫자 데이터의 원천이라기보다 사용자가 자주 신뢰하거나 참고하는 해설/리포트의 최신 업데이트를 한눈에 보여준다.
- 각 항목은 제목, 날짜, source, 관련 태그, 한 줄 요약, 원문 링크, refresh_status를 가진다.
- 자동 요약을 붙일 경우에는 원문 링크와 fetched_at을 함께 표시하고, 요약이 원문 수치를 대체하지 않도록 한다.

초기 favorite source matrix:

| 소스 | 성격 | 접근 방식 후보 | 현재 연결 상태 | 대시보드 표시 방식 |
|---|---|---|---|---|
| 한국은행 리포트 | 공식/공공 매크로·산업 분석 | BOK 홈페이지 게시판 HTML/RSS 후보, 필요 시 게시판 scrape | 확인: bok.or.kr 접근 가능. 세부 게시판 endpoint는 구현 시 확정 | 최신 리포트 5개, 반도체/AI/수출/금리 키워드 매칭, official/public_source |
| 슈카월드 리포트 | 해설/동영상 commentary | YouTube RSS `https://www.youtube.com/feeds/videos.xml?channel_id=UCsJ6RuBiTVWRX156FVbeaGg` | 확인: RSS 접근 가능 | 최신 영상, 제목/게시일/링크, 반도체/AI/매크로 키워드 태그, commentary_source |
| 토스증권 리포트 | 증권사/투자자용 commentary | tossinvest.com/토스피드/앱 리포트 URL 후보. 공개 feed/API는 추가 확인 필요 | 부분 확인: tossinvest.com, tossfeed 접근 가능. 리포트 전용 공개 endpoint는 미확정 | endpoint 확정 전에는 manual_real/bookmark_source로 시작하고, 가짜 기사 생성 금지 |

### 19.5 데이터 모델 추가

#### value_chain_companies

- theme: fabless, foundry, memory, substrate_materials
- company
- ticker
- country
- exchange
- role_note
- representative_rank
- source_name
- source_url
- refresh_status

#### theme_daily

- date
- theme
- basket_return_1d
- basket_return_1m
- basket_return_ytd
- representative_tickers
- source_dependencies
- refresh_status
- quality_note

#### company_status

- date
- theme
- company
- ticker
- price
- return_1d
- return_1m
- return_ytd
- latest_revenue
- latest_margin
- segment_or_ai_revenue_note
- market_share_value nullable
- market_share_unit nullable
- market_share_source_type: official, company_ir, paid_vendor, manual_real, proxy_real, unavailable
- latest_news_title
- latest_news_url
- source_name
- fetched_at
- refresh_status
- quality_note

#### favorite_source_items

- source_key: bok, shuka_world, toss_securities
- source_name
- item_id
- title
- published_at
- url
- tags
- summary_short
- related_companies
- related_themes
- source_type: official_public, commentary, brokerage_commentary, manual_real
- fetched_at
- refresh_status
- quality_note

### 19.6 수집 전략

Phase A: 실제 가격/실적 기반 AI 칩 체인 MVP

1. `config/value_chain_companies.json` 생성
2. Yahoo/Naver 가격 수집기에 NVIDIA, AMD, Marvell, Qualcomm, Arm, Samsung Electro-Mechanics 등 대표 tickers 추가
3. SEC companyfacts로 NVIDIA/AMD/Marvell/Qualcomm/Intel 등 미국 기업의 revenue/gross profit/net income fact 추가
4. 한국 기업은 OPENDART key 전까지 가격 중심 + IR/manual_real fact로 표시
5. 테마 바스켓 수익률을 실제 가격 series에서 계산
6. 점유율은 연결 가능한 공식/IR/유료/수동 실제 소스가 없으면 `unavailable`로 둔다.

Phase B: Favorite 소스 수집

1. 슈카월드는 YouTube RSS로 자동 수집한다.
2. 한국은행은 BOK 게시판 후보를 확정하고 HTML/RSS scrape를 구현한다.
3. 토스증권은 공개 endpoint를 추가 조사한다. 확정 전에는 사용자가 중요 링크를 `config/favorite_sources.json`에 넣는 manual_real 방식으로 시작한다.
4. 각 item은 키워드 필터링만 하고, 투자 판단 수치로 쓰지 않는다.

Phase C: UI 반영

1. 좌측 메뉴에 `AI 칩 체인`, `Favorite 소스` 추가
2. 첫 화면 하단 또는 별도 탭에 밸류체인 온도맵 추가
3. Favorite 소스는 우측 레일 또는 별도 탭에서 최신 5~10개 표시
4. 모든 item에 source/fetched_at/refresh_status 표시

### 19.7 No-mock / 증거 경계

- 뉴스나 리포트가 없으면 빈 상태 또는 `manual_required`를 표시한다.
- 슈카월드/토스증권은 commentary source이며 공식 수치 원천처럼 표시하지 않는다.
- 점유율 수치는 출처가 없으면 만들지 않는다.
- AI chip theme score는 실제 가격/실적/news availability에서 계산하고, 가중치는 문서화한다.
- 토스증권 리포트 접근이 앱/로그인에 막히면 자동 수집을 주장하지 않고 manual_real link list로 시작한다.

### 19.8 구현 전 acceptance criteria

- `dashboard.json` 또는 후속 `value_chain.json`에 `mock_data=false`
- AI 칩 체인 탭에 4개 테마가 모두 표시됨
- 각 테마마다 최소 2개 이상 대표 기업이 실제 ticker/source와 연결됨
- Favorite 소스 패널에 BOK, 슈카월드, 토스증권 3개 source row가 보임
- 슈카월드 RSS는 자동 수집 ok 또는 실패 상태를 표시함
- 한국은행/토스증권은 endpoint 확정 전에도 fake item을 생성하지 않음
- 모든 뉴스/리포트 item에 `source_type`, `url`, `published_at`, `fetched_at`, `refresh_status`가 있음

## 20. 최소 공수 No-key MVP 데이터 전략

### 20.1 결론

초기 운영은 API key 없이도 가능하다. 다만 데이터의 등급을 명확히 구분한다.

- **자동 no-key로 충분히 가능한 것**: 가격/지수/환율 일부, 미국 기업 SEC 실적 fact, 슈카월드 RSS, TSMC 월매출 페이지, 한국은행 공개 HTML 페이지
- **no-key로 가능하지만 공식/계약 API는 아닌 것**: Yahoo Finance chart, Naver Stock chart JSON
- **no-key로 자동화가 애매한 것**: 한국은행 세부 리포트 게시판 scrape, 토스증권 리포트, 한국 수출 상세 원자료
- **no-key로 억지 자동화하지 않을 것**: DRAM/NAND/HBM spot/contract 가격, 유료 점유율 데이터, 개인 포트폴리오 서버 저장

따라서 MVP는 `no_key_auto` + `manual_real` 조합으로 시작한다. API key가 필요한 OPENDART, BOK ECOS, FRED API, data.go.kr, 유료 메모리 가격은 후순위로 둔다.

### 20.2 No-key MVP 소스 매트릭스

| 영역 | 데이터 | no-key 소스 후보 | 현재 확인 | 운영 등급 | 표시 방식 |
|---|---|---|---|---|---|
| 한국 가격 | KOSPI, 삼성전자, SK하이닉스, 삼성전기 등 | Naver Stock chart JSON | 확인됨: KOSPI, 005930, 000660, 009150 응답 ok | `no_key_auto_provider` | 실제 가격 카드. KRX 공식 API가 아님을 quality_note에 표시 |
| 글로벌 가격 | NVIDIA, AMD, TSMC, Broadcom, Micron, SOX, USD/KRW 등 | Yahoo Finance chart JSON | 확인됨: NVDA, TSM/2330.TW 등 응답 ok | `no_key_auto_provider` | 실제 가격/바스켓 수익률. 비공식 무료 provider 한계 표시 |
| 미국 기업 실적 fact | NVIDIA, AMD, Broadcom, Micron 등 revenue/gross profit/net income | SEC EDGAR companyfacts API | 확인됨: NVIDIA, AMD, Broadcom, Micron 가능 | `official_no_key_public_api` | 실적 fact 카드. AI segment 매출은 별도 IR/manual 필요 |
| 미국 금리 | 미국 국채 수익률 | US Treasury XML | 확인됨: Treasury daily rates XML 응답 ok | `official_no_key_public_api` | 금리 카드. FRED API key 없이 대체 가능 |
| 슈카월드 | 최신 영상/제목/날짜/링크 | YouTube RSS | 확인됨: channel RSS 응답 ok | `commentary_no_key_rss` | Favorite 소스. 공식 수치가 아닌 commentary로 표시 |
| 한국은행 | 리포트/보도자료/게시글 | bok.or.kr HTML 게시판 | 메인/게시판 접근 확인. 세부 게시판은 구현 시 확정 | `official_no_key_html` 또는 `manual_real` | Favorite 소스. scrape 실패 시 manual_required |
| TSMC 월매출 | 월매출 페이지 | TSMC IR HTML | 확인됨: monthly revenue page 응답 ok | `company_ir_no_key_html` | 자동 파싱 가능하면 사용. 구조 변경 시 failed/manual_required |
| 토스증권 | 리포트/해설 | tossinvest.com, tossfeed, 사용자가 지정한 링크 | 사이트 접근은 확인. 리포트 전용 feed/API 미확정 | `manual_real` 우선 | 자동 수집 주장 금지. 링크 모음/북마크로 시작 |
| 한국 수출 | 반도체 수출 YoY/MoM | MOTIR 보도자료 HTML, 관세청/공공데이터 수동 CSV | API key 없이 보도자료 scrape 가능성 있음 | `manual_real` 우선, 이후 `official_no_key_html` 후보 | 숫자 자동 파싱 전에는 수동 입력/출처 링크 표시 |
| 메모리 가격 | DRAM/NAND/HBM spot/contract | 유료 vendor 또는 사용자가 올린 실제 CSV | 무료 안정 API 없음 | `paid_required` 또는 `manual_real` | fake 가격 금지. unavailable/manual_required |
| 점유율 | foundry/HBM/DRAM/fabless share | TrendForce/Omdia/Gartner/기업 IR | 무료 안정 API 없음 | `paid_required`, `company_ir`, `proxy_real`, `manual_real` | 출처 있는 값만 표시. 없으면 unavailable |
| 포트폴리오 | 보유 비중/손익 | 브라우저 로컬 CSV import | 서버 저장 불필요 | `local_only_manual_real` | public JSON에 넣지 않음 |

### 20.3 최소 공수 구현 우선순위

1. **가격/바스켓 먼저**
   - Naver + Yahoo no-key chart로 AI 칩 체인 대표 기업 가격과 1D/1M/YTD 수익률을 채운다.
   - 이 단계만으로도 팹리스/파운드리/메모리/기판소재 온도맵은 구현 가능하다.

2. **SEC 실적 fact 추가**
   - 미국 기업은 SEC companyfacts no-key로 revenue/gross profit/net income을 채운다.
   - AI segment revenue는 companyfacts에 항상 있는 값이 아니므로 IR/manual_real로 분리한다.

3. **Favorite 소스는 쉬운 것부터**
   - 슈카월드: YouTube RSS 자동
   - 한국은행: 우선 BOK HTML 링크/제목 scrape 또는 수동 favorite link list
   - 토스증권: 전용 공개 endpoint 확인 전까지 manual_real/bookmark list

4. **어려운 데이터는 비워둔다**
   - DRAM/NAND/HBM spot 가격, 시장 점유율, 유료 리포트 수치는 만들지 않는다.
   - 화면에는 `manual_required`, `paid_required`, `unavailable`로 표시한다.

### 20.4 API key를 뒤로 미뤄도 되는 이유

- 대시보드의 첫 가치는 “정확한 모든 산업 데이터”가 아니라 “AI 반도체 체인의 온도와 방향을 빠르게 보는 것”이다.
- 가격, 바스켓 수익률, SEC 실적 fact, favorite source 업데이트만으로도 첫 유용 버전이 가능하다.
- API key 기반 공식 데이터는 이후 정확도/신뢰도 개선 단계에서 붙인다.
- key 없는 provider는 언제든 실패할 수 있으므로, 실패 시 fake 대체 없이 `failed`를 표시한다.

### 20.5 No-key MVP acceptance criteria

- API key 없이 `python scripts/fetch_dashboard_data.py --out public/data/dashboard.json` 실행 가능
- `mock_data=false`
- 가격 카드 최소 8개 이상 `refresh_status=ok`
- AI 칩 체인 4개 테마 모두 대표 ticker 2개 이상 연결
- 슈카월드 RSS item 자동 수집 또는 실패 상태 표시
- 한국은행/토스증권은 자동 endpoint 미확정 시 manual_real source row 표시
- DRAM/NAND/HBM 가격과 점유율은 출처가 없으면 숫자를 표시하지 않음
