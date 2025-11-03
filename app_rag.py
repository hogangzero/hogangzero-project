from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 한글 폰트 등록 (시스템에 따라 경로 수정 필요)
try:
    pdfmetrics.registerFont(TTFont('NanumGothic', '/System/Library/Fonts/Supplemental/AppleGothic.ttf'))
    font_name = 'NanumGothic'
except:
    try:
        pdfmetrics.registerFont(TTFont('Malgun', 'c:/windows/fonts/malgun.ttf'))
        font_name = 'Malgun'
    except:
        font_name = 'Helvetica'

# PDF 생성
pdf_filename = "호갱제로_사용설명서.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                    rightMargin=2*cm, leftMargin=2*cm,
                    topMargin=2*cm, bottomMargin=2*cm)

# 스타일 설정
styles = getSampleStyleSheet()

# 커스텀 스타일 생성
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontName=font_name,
    fontSize=24,
    textColor=colors.HexColor('#667eea'),
    spaceAfter=30,
    alignment=TA_CENTER,
    bold=True
)

heading1_style = ParagraphStyle(
    'CustomHeading1',
    parent=styles['Heading1'],
    fontName=font_name,
    fontSize=18,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=12,
    spaceBefore=20,
    bold=True
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontName=font_name,
    fontSize=14,
    textColor=colors.HexColor('#667eea'),
    spaceAfter=10,
    spaceBefore=15,
    bold=True
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontName=font_name,
    fontSize=11,
    leading=18,
    alignment=TA_JUSTIFY,
    spaceAfter=10
)

bullet_style = ParagraphStyle(
    'CustomBullet',
    parent=styles['BodyText'],
    fontName=font_name,
    fontSize=11,
    leading=16,
    leftIndent=20,
    spaceAfter=8
)

# PDF 내용 구성
story = []

# 표지
story.append(Spacer(1, 3*cm))
story.append(Paragraph("호갱제로", title_style))
story.append(Paragraph("투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션", 
                       ParagraphStyle('subtitle', parent=body_style, alignment=TA_CENTER, 
                                    fontSize=14, textColor=colors.HexColor('#764ba2'))))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("사용설명서", 
                       ParagraphStyle('version', parent=body_style, alignment=TA_CENTER, 
                                    fontSize=12, textColor=colors.grey)))
story.append(Spacer(1, 2*cm))

# 시스템 정보 테이블
info_data = [
    ['데이터 출처', '수산물유통정보시스템(FIPS), 해양환경정보시스템'],
    ['데이터 기간', '2021년 ~ 2024년'],
    ['업데이트', '실시간 연동'],
    ['문의', 'support@hogaengzero.com']
]
info_table = Table(info_data, colWidths=[4*cm, 12*cm])
info_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f7fa')),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('TOPPADDING', (0, 0), (-1, -1), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
]))
story.append(info_table)
story.append(PageBreak())

# 목차
story.append(Paragraph("목차", heading1_style))
story.append(Spacer(1, 0.5*cm))

toc_data = [
    ['1. 시스템 개요', '3'],
    ['2. 홈 화면', '4'],
    ['3. 시세 알아보기', '6'],
    ['  3-1. 어종별 시세', '6'],
    ['  3-2. 산지별 시세', '8'],
    ['4. 시세 예측하기', '10'],
    ['  4-1. 날짜별 예측', '10'],
    ['  4-2. 상세 검색 예측', '12'],
    ['5. AI 챗봇 기능', '14'],
    ['6. 자주 묻는 질문(FAQ)', '15'],
    ['7. 문제 해결 가이드', '16']
]

toc_table = Table(toc_data, colWidths=[14*cm, 2*cm])
toc_table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey)
]))
story.append(toc_table)
story.append(PageBreak())

# 1. 시스템 개요
story.append(Paragraph("1. 시스템 개요", heading1_style))
story.append(Paragraph(
    "호갱제로는 수산물 도매 시장의 투명성을 높이고 합리적인 거래를 지원하기 위한 AI 기반 데이터 분석 플랫폼입니다. "
    "실시간 경매가 정보, 산지별 가격 비교, AI 가격 예측 기능을 제공하여 수산물 거래자들의 의사결정을 돕습니다.",
    body_style
))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("1.1 주요 기능", heading2_style))
story.append(Paragraph("• 어종별 실시간 시세 조회 및 분석", bullet_style))
story.append(Paragraph("• 산지별 가격 비교 및 최적 거래처 추천", bullet_style))
story.append(Paragraph("• AI 기반 미래 가격 예측 (날짜별/맞춤형)", bullet_style))
story.append(Paragraph("• 해양환경 데이터 연계 분석", bullet_style))
story.append(Paragraph("• 24시간 AI 챗봇 상담 서비스", bullet_style))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("1.2 사용 데이터", heading2_style))
story.append(Paragraph(
    "본 시스템은 수산물유통정보시스템(FIPS)과 해양환경정보시스템의 공공 데이터를 활용합니다. "
    "2021년부터 2024년까지의 경매 데이터와 수온, 기온, 풍속 등 해양환경 데이터를 통합하여 "
    "정확한 분석과 예측을 제공합니다.",
    body_style
))
story.append(PageBreak())

# 2. 홈 화면
story.append(Paragraph("2. 홈 화면", heading1_style))
story.append(Paragraph(
    "홈 화면은 호갱제로의 메인 대시보드로, 주요 기능과 최신 시세 정보를 한눈에 확인할 수 있습니다.",
    body_style
))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("2.1 주요 지표 카드", heading2_style))
story.append(Paragraph("• 등록 어종: 시스템에 등록된 전체 어종 수", bullet_style))
story.append(Paragraph("• 거래 산지: 전국 거래 산지 수", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("2.2 최근 가격 추이", heading2_style))
story.append(Paragraph(
    "최근 7일간 거래량이 많은 상위 6개 어종의 30일 가격 추이를 미니 차트로 표시합니다. "
    "각 차트에는 최신 가격과 전일 대비 변동률이 표시되어 시장 동향을 빠르게 파악할 수 있습니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("2.3 제철 어종 추천", heading2_style))
story.append(Paragraph(
    "현재 월을 기준으로 전월, 이번 달, 다음 달의 제철 어종을 추천합니다. "
    "제철 어종은 월별 최저 평균가를 기준으로 선정되며, 각 어종의 평균 가격이 함께 표시됩니다.",
    body_style
))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("2.4 AI 챗봇 기능", heading2_style))
story.append(Paragraph("홈 화면에서는 두 가지 AI 챗봇 기능을 제공합니다:", body_style))
story.append(Paragraph("• 실시간 시세 상담 챗봇: Google API 기반 실시간 수산물 시세 조회", bullet_style))
story.append(Paragraph("• 전문 지식 상담 챗봇: RAG 기반 수산물 유통, 보관, 품질 관리 정보 제공", bullet_style))
story.append(PageBreak())

# 3. 시세 알아보기
story.append(Paragraph("3. 시세 알아보기", heading1_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.1 어종별 시세", heading2_style))
story.append(Paragraph(
    "특정 어종의 상세한 가격 정보와 추이를 분석할 수 있는 기능입니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.1.1 어종별 평균 경매가", heading2_style))
story.append(Paragraph("사용 방법:", body_style))
story.append(Paragraph("1. 셀렉트박스에서 분석할 어종을 선택합니다", bullet_style))
story.append(Paragraph("2. '시세 보기' 버튼을 클릭하여 데이터를 조회합니다", bullet_style))
story.append(Paragraph("3. 일별 경매가 데이터 테이블이 표시됩니다", bullet_style))
story.append(Paragraph("4. 평균가, 낙찰고가, 낙찰저가 중 원하는 항목을 선택합니다", bullet_style))
story.append(Paragraph("5. 선택한 항목의 가격 추이 그래프가 생성됩니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("표시 정보:", body_style))
story.append(Paragraph("• 평균 경매가: 전체 기간 평균 및 최근 추세", bullet_style))
story.append(Paragraph("• 최고 낙찰가: 최고가 및 평균 대비 비율", bullet_style))
story.append(Paragraph("• 최저 낙찰가: 최저가 및 평균 대비 비율", bullet_style))
story.append(Paragraph("• 가격 변동폭: 최고가-최저가 범위 및 변동률", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.1.2 품종 및 상태별 어종 경매가", heading2_style))
story.append(Paragraph(
    "동일 어종의 활어, 냉동, 선어(냉장) 상태별 가격을 비교할 수 있습니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("사용 방법:", body_style))
story.append(Paragraph("1. 어종을 선택합니다 (데이터가 100개 이상인 어종만 표시)", bullet_style))
story.append(Paragraph("2. '비교 보기' 버튼을 클릭합니다", bullet_style))
story.append(Paragraph("3. 품종을 선택합니다 (최대 2개)", bullet_style))
story.append(Paragraph("4. 각 품종의 상태를 선택합니다 (활어/냉동/선어)", bullet_style))
story.append(Paragraph("5. 선택한 품종의 가격 비교 그래프가 생성됩니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("분석 정보:", body_style))
story.append(Paragraph("• 최근 가격 동향: 최근 30일 평균 vs 전체 평균", bullet_style))
story.append(Paragraph("• 가격 변동성: 가격 안정성 평가 (낮음/중간/높음)", bullet_style))
story.append(Paragraph("• 최적 거래 시기: 월별 최저가/최고가 분석", bullet_style))
story.append(PageBreak())

story.append(Paragraph("3.1.3 해양데이터 관계 분석", heading2_style))
story.append(Paragraph(
    "수온, 기온, 풍속 등 해양환경 데이터와 어종 가격의 상관관계를 분석합니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("사용 방법:", body_style))
story.append(Paragraph("1. '분석 보기' 버튼을 클릭합니다", bullet_style))
story.append(Paragraph("2. 산지를 선택합니다", bullet_style))
story.append(Paragraph("3. 어종을 선택합니다", bullet_style))
story.append(Paragraph("4. 비교할 해양 변수를 선택합니다 (수온/기온/풍속)", bullet_style))
story.append(Paragraph("5. 월별 평균가와 해양데이터의 관계 그래프가 표시됩니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("제공 정보:", body_style))
story.append(Paragraph("• 환경별 관계 1순위 어종: 각 환경 변수별로 가장 영향을 많이 받는 어종", bullet_style))
story.append(Paragraph("• 수온 영향: 수온과 가격의 상관관계 분석", bullet_style))
story.append(Paragraph("• 계절별 시세: 봄/여름/가을/겨울 계절별 가격 패턴", bullet_style))
story.append(Paragraph("• 풍속 영향도: 풍속이 가격에 미치는 영향 정도", bullet_style))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("3.2 산지별 시세", heading2_style))
story.append(Paragraph(
    "특정 산지의 어종별 가격 정보를 조회하고 산지 간 가격을 비교합니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.2.1 산지별 어종 평균 경매가", heading2_style))
story.append(Paragraph("사용 방법:", body_style))
story.append(Paragraph("1. 셀렉트박스에서 산지를 선택합니다", bullet_style))
story.append(Paragraph("2. 해당 산지에서 취급하는 모든 어종의 평균 가격 막대그래프가 표시됩니다", bullet_style))
story.append(Paragraph("3. 각 어종의 가격을 비교하여 산지 특화 어종을 파악할 수 있습니다", bullet_style))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("3.2.2 인기 어종 Top 10 산지별 시세", heading2_style))
story.append(Paragraph(
    "거래량이 많은 상위 10개 어종의 산지별 월별 가격 추이를 비교합니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("사용 방법:", body_style))
story.append(Paragraph("1. 품종을 선택합니다 (거래량 Top 10 어종)", bullet_style))
story.append(Paragraph("2. 산지를 선택합니다 (해당 품종 거래량 상위 5곳)", bullet_style))
story.append(Paragraph("3. 월별 평균 경매가 그래프가 표시됩니다", bullet_style))
story.append(Paragraph("4. 최고가/최저가 월이 그래프에 표시됩니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("제공 메트릭:", body_style))
story.append(Paragraph("• 평균 경매가: 전체 기간 평균 가격", bullet_style))
story.append(Paragraph("• 최대 가격차: 최고가-최저가 및 변동률", bullet_style))
story.append(Paragraph("• 거래 건수: 해당 조건의 총 거래 건수", bullet_style))
story.append(PageBreak())

# 4. 시세 예측하기
story.append(Paragraph("4. 시세 예측하기", heading1_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("4.1 날짜별 예측", heading2_style))
story.append(Paragraph(
    "Prophet 알고리즘을 활용하여 특정 어종의 미래 가격을 예측합니다. "
    "과거 데이터의 계절성과 트렌드를 학습하여 향후 1~5년간의 월별 가격을 예측합니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("사용 방법:", heading2_style))
story.append(Paragraph("1. 사이드바에서 분석할 어종을 선택합니다", bullet_style))
story.append(Paragraph("2. 예측 연도를 설정합니다 (1~5년)", bullet_style))
story.append(Paragraph("3. 주요 거래월을 선택합니다 (복수 선택 가능)", bullet_style))
story.append(Paragraph("4. 시스템이 자동으로 모델을 학습하거나 기존 모델을 로드합니다", bullet_style))
story.append(Paragraph("5. 예측 결과가 자동으로 생성됩니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("4.1.1 최근 시장 경매가", heading2_style))
story.append(Paragraph(
    "최근 12개월의 실제 거래 데이터를 테이블로 표시합니다. "
    "현재 시장 상황을 파악하고 예측 결과와 비교할 수 있습니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("4.1.2 경매가 예측 데이터", heading2_style))
story.append(Paragraph("예측 결과에는 다음 정보가 포함됩니다:", body_style))
story.append(Paragraph("• 거래월: 예측 대상 연월", bullet_style))
story.append(Paragraph("• 예측가격: AI가 예측한 평균 경매가", bullet_style))
story.append(Paragraph("• 최소예상가격: 신뢰구간 하한선 (5 percentile)", bullet_style))
story.append(Paragraph("• 최대예상가격: 신뢰구간 상한선 (95 percentile)", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("4.1.3 예측 시세 그래프", heading2_style))
story.append(Paragraph(
    "Plotly 인터랙티브 차트로 예측 결과를 시각화합니다. "
    "마우스를 올리면 상세 정보를 확인할 수 있으며, 확대/축소가 가능합니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("그래프 요소:", body_style))
story.append(Paragraph("• 실제 거래가: 초록색 선과 점으로 표시된 과거 실제 데이터", bullet_style))
story.append(Paragraph("• 예측 가격: 보라색 점선으로 표시된 미래 예측값", bullet_style))
story.append(Paragraph("• 신뢰구간: 연보라색 영역으로 표시된 예측 불확실성 범위", bullet_style))
story.append(Paragraph("• 예측 구간: 노란색 배경으로 강조된 미래 예측 기간", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("4.1.4 주요 거래월 예상 경매가", heading2_style))
story.append(Paragraph(
    "선택한 주요 거래월의 예상 가격을 카드 형태로 표시합니다. "
    "각 카드에는 예측가격, 전월 대비 변동률, 변동 범위가 표시됩니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("카드 정보:", body_style))
story.append(Paragraph("• 상승 추세: 📈 빨간색으로 표시", bullet_style))
story.append(Paragraph("• 하락 추세: 📉 초록색으로 표시", bullet_style))
story.append(Paragraph("• 안정 추세: ➖ 회색으로 표시", bullet_style))
story.append(PageBreak())

story.append(Paragraph("4.2 상세 검색 예측 (맞춤형 예측)", heading2_style))
story.append(Paragraph(
    "Random Forest 알고리즘을 활용하여 구체적인 거래 조건에 따른 맞춤형 가격을 예측합니다. "
    "어종, 원산지, 규격, 포장, 수량, 중량 등 다양한 조건을 입력하여 정확한 가격을 산출합니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("사용 방법:", heading2_style))
story.append(Paragraph("1. 사이드바에서 거래 조건을 입력합니다:", bullet_style))
story.append(Paragraph("   - 어종 선택", bullet_style))
story.append(Paragraph("   - 원산지 선택", bullet_style))
story.append(Paragraph("   - 규격 등급 선택", bullet_style))
story.append(Paragraph("   - 포장 형태 선택", bullet_style))
story.append(Paragraph("   - 수량 입력 (단위)", bullet_style))
story.append(Paragraph("   - 중량 입력 (kg)", bullet_style))
story.append(Paragraph("2. 입력한 거래 조건이 메인 화면에 표로 정리되어 표시됩니다", bullet_style))
story.append(Paragraph("3. '맞춤 가격 예측하기' 버튼을 클릭합니다", bullet_style))
story.append(Paragraph("4. AI가 해당 조건의 예상 경매가를 계산합니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("예측 결과:", heading2_style))
story.append(Paragraph("• 예측 경매가: 입력한 조건의 예상 가격", bullet_style))
story.append(Paragraph("• 예측 신뢰 구간: 5%~95% 신뢰수준의 가격 범위", bullet_style))
story.append(Paragraph("• CSV 다운로드: 예측 결과를 파일로 저장 가능", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("AI 분석 정보:", heading2_style))
story.append(Paragraph(
    "주요 가격 영향 요인 그래프가 표시됩니다. "
    "이 그래프는 AI 모델이 학습한 결과를 바탕으로 어떤 요인이 가격 결정에 가장 큰 영향을 미치는지 보여줍니다. "
    "높은 퍼센트일수록 해당 요인의 영향력이 큽니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("주의사항:", heading2_style))
story.append(Paragraph("• 규격, 수량, 원산지 등을 신중히 선택하여 정확한 예측을 받으세요", bullet_style))
story.append(Paragraph("• 예측 모델은 과거 데이터를 기반으로 학습되므로, 급격한 시장 변화는 반영되지 않을 수 있습니다", bullet_style))
story.append(Paragraph("• 신뢰구간을 참고하여 가격 변동성을 고려한 의사결정을 하세요", bullet_style))
story.append(PageBreak())

# 5. AI 챗봇 기능
story.append(Paragraph("5. AI 챗봇 기능", heading1_style))
story.append(Paragraph(
    "호갱제로는 우측 하단의 '챗봇 문의' 버튼을 통해 24시간 AI 챗봇 서비스를 제공합니다. "
    "시스템 사용법, 데이터 해석, 수산물 관련 전문 지식 등을 실시간으로 상담받을 수 있습니다.",
    body_style
))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("5.1 챗봇 실행 방법", heading2_style))
story.append(Paragraph("1. 화면 우측 하단의 '챗봇 문의' 버튼을 클릭합니다", bullet_style))
story.append(Paragraph("2. 챗봇 창이 팝업 형태로 나타납니다", bullet_style))
story.append(Paragraph("3. 질문을 입력하고 Enter 키를 누릅니다", bullet_style))
story.append(Paragraph("4. AI가 답변을 생성하여 표시합니다", bullet_style))
story.append(Paragraph("5. '챗봇 닫기' 버튼으로 챗봇 창을 닫을 수 있습니다", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("5.2 실시간 시세 상담 챗봇", heading2_style))
story.append(Paragraph(
    "Google API 기반으로 실시간 수산물 시세를 조회하고 가격 분석을 제공합니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("활용 예시:", body_style))
story.append(Paragraph("• '오늘 갈치 시세가 어떻게 되나요?'", bullet_style))
story.append(Paragraph("• '제주산 광어 가격이 얼마인가요?'", bullet_style))
story.append(Paragraph("• '이번 주 전복 가격 추이를 알려주세요'", bullet_style))
story.append(Paragraph("• '최근 고등어 가격이 왜 올랐나요?'", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("5.3 전문 지식 상담 챗봇 (RAG 기반)", heading2_style))
story.append(Paragraph(
    "RAG(Retrieval-Augmented Generation) 기술을 활용하여 수산물 유통, 보관, 품질 관리 등 "
    "전문적인 정보를 제공합니다. 본 사용설명서의 내용도 학습되어 있어 시스템 사용법을 쉽게 안내받을 수 있습니다.",
    body_style
))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("활용 예시:", body_style))
story.append(Paragraph("• '어종별 시세 분석은 어떻게 사용하나요?'", bullet_style))
story.append(Paragraph("• '날짜별 예측과 맞춤형 예측의 차이가 뭔가요?'", bullet_style))
story.append(Paragraph("• '해양데이터 관계 분석 기능을 설명해주세요'", bullet_style))
story.append(Paragraph("• '수산물 보관 온도는 어떻게 관리하나요?'", bullet_style))
story.append(Paragraph("• '활어 운송 시 주의사항을 알려주세요'", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("5.4 챗봇 활용 팁", heading2_style))
story.append(Paragraph("• 구체적인 질문일수록 정확한 답변을 받을 수 있습니다", bullet_style))
story.append(Paragraph("• 어종명, 산지명, 날짜 등을 명확히 입력하세요", bullet_style))
story.append(Paragraph("• 한 번에 여러 질문보다는 하나씩 질문하는 것이 효과적입니다", bullet_style))
story.append(Paragraph("• 챗봇이 이해하지 못한 경우 다른 표현으로 다시 질문해보세요", bullet_style))
story.append(Paragraph("• 시스템 사용법은 '~는 어떻게 사용하나요?' 형태로 질문하세요", bullet_style))
story.append(PageBreak())

# 6. 자주 묻는 질문 (FAQ)
story.append(Paragraph("6. 자주 묻는 질문 (FAQ)", heading1_style))
story.append(Spacer(1, 0.3*cm))

faq_items = [
    ("Q1. 데이터는 얼마나 자주 업데이트되나요?", 
    "A1. 수산물유통정보시스템(FIPS)의 데이터를 기반으로 하며, 2021년부터 2024년까지의 누적 데이터를 사용합니다. "
    "실시간 연동은 아니지만, 주기적으로 최신 데이터를 반영합니다."),
    
    ("Q2. 예측 가격의 정확도는 어느 정도인가요?", 
    "A2. 과거 데이터 패턴을 기반으로 한 통계적 예측이므로, 가까운 미래일수록 정확도가 높습니다. "
    "급격한 시장 변화나 예상치 못한 이벤트는 반영되지 않을 수 있으므로, 참고 자료로 활용하시기 바랍니다."),
    
    ("Q3. 원양 산지와 일반 산지의 차이는 무엇인가요?", 
    "A3. 원양 산지는 '(원양)'으로 표시되며, 국내가 아닌 해외 원양에서 어획한 수산물을 취급하는 산지입니다. "
    "일반 산지는 국내 연안이나 양식장에서 생산된 수산물을 취급합니다."),
    
    ("Q4. 신뢰구간이란 무엇인가요?", 
    "A4. 예측 가격이 위치할 것으로 예상되는 범위입니다. "
    "95% 신뢰수준에서 5%~95% 범위 내에 실제 가격이 위치할 확률이 높습니다. "
    "신뢰구간이 넓을수록 예측 불확실성이 크다는 의미입니다."),
    
    ("Q5. 어종별 시세와 산지별 시세의 차이는 무엇인가요?", 
    "A5. 어종별 시세는 특정 어종의 가격을 중심으로 분석하며, 산지별 시세는 특정 산지를 중심으로 "
    "해당 지역의 어종별 가격을 분석합니다. 목적에 따라 선택하여 사용하세요."),
    
    ("Q6. 주요 거래월은 어떻게 선택하나요?", 
    "A6. 본인이 주로 거래하는 시기나 관심 있는 월을 선택하면 됩니다. "
    "일반적으로 분기별(3,6,9,12월) 또는 성수기/비수기를 고려하여 선택합니다."),
    
    ("Q7. 해양환경 데이터는 왜 분석하나요?", 
    "A7. 수온, 기온, 풍속 등 해양환경은 수산물의 어획량과 품질에 직접적인 영향을 미쳐 "
    "가격 변동의 원인이 됩니다. 이러한 상관관계를 파악하면 가격 변동을 미리 예측할 수 있습니다."),
    
    ("Q8. CSV 다운로드 기능은 어디에 있나요?", 
    "A8. 맞춤형 가격 예측 결과 하단에 '예측 결과 다운로드 (CSV)' 버튼이 있습니다. "
    "예측 결과를 CSV 파일로 저장하여 엑셀 등에서 활용할 수 있습니다."),
    
    ("Q9. 모바일에서도 사용할 수 있나요?", 
    "A9. 네, 웹 기반 시스템이므로 모바일 브라우저에서도 접속하여 사용할 수 있습니다. "
    "다만, 화면 크기가 작아 일부 차트나 테이블이 보기 불편할 수 있습니다."),
    
    ("Q10. 챗봇이 답변하지 못하는 경우는 어떻게 하나요?", 
    "A10. 질문을 다른 표현으로 바꿔보거나, 더 구체적으로 질문해보세요. "
    "그래도 해결되지 않으면 support@hogaengzero.com으로 문의해주시기 바랍니다.")
]

for q, a in faq_items:
    story.append(Paragraph(q, 
        ParagraphStyle('question', parent=body_style, fontSize=12, 
                    textColor=colors.HexColor('#667eea'), fontName=font_name, bold=True)))
    story.append(Paragraph(a, body_style))
    story.append(Spacer(1, 0.3*cm))

story.append(PageBreak())

# 7. 문제 해결 가이드
story.append(Paragraph("7. 문제 해결 가이드", heading1_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("7.1 데이터가 표시되지 않는 경우", heading2_style))
story.append(Paragraph("증상: 그래프나 테이블에 데이터가 나타나지 않습니다.", body_style))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("해결 방법:", body_style))
story.append(Paragraph("• 선택한 어종이나 산지에 충분한 데이터가 있는지 확인하세요 (최소 100개)", bullet_style))
story.append(Paragraph("• '초기화' 버튼을 눌러 선택을 재설정해보세요", bullet_style))
story.append(Paragraph("• 브라우저를 새로고침(F5)하여 다시 시도하세요", bullet_style))
story.append(Paragraph("• 다른 어종이나 산지를 선택해보세요", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("7.2 그래프가 제대로 그려지지 않는 경우", heading2_style))
story.append(Paragraph("증상: 차트가 깨지거나 이상하게 표시됩니다.", body_style))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("해결 방법:", body_style))
story.append(Paragraph("• 브라우저 캐시를 삭제하고 페이지를 새로고침하세요", bullet_style))
story.append(Paragraph("• 다른 브라우저(Chrome, Edge, Firefox)에서 접속해보세요", bullet_style))
story.append(Paragraph("• 화면 크기를 조정하거나 확대/축소를 100%로 설정하세요", bullet_style))
story.append(Paragraph("• 인터넷 연결 상태를 확인하세요", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("7.3 예측이 실행되지 않는 경우", heading2_style))
story.append(Paragraph("증상: 예측 버튼을 눌러도 결과가 나타나지 않습니다.", body_style))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("해결 방법:", body_style))
story.append(Paragraph("• 모델 학습 중일 수 있으니 잠시 기다려주세요 (최대 1분)", bullet_style))
story.append(Paragraph("• 맞춤형 예측의 경우 모든 필수 항목을 입력했는지 확인하세요", bullet_style))
story.append(Paragraph("• 수량과 중량에 0이 아닌 양수를 입력했는지 확인하세요", bullet_style))
story.append(Paragraph("• 페이지를 새로고침하고 다시 시도하세요", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("7.4 챗봇이 응답하지 않는 경우", heading2_style))
story.append(Paragraph("증상: 챗봇에 질문을 입력해도 답변이 없습니다.", body_style))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("해결 방법:", body_style))
story.append(Paragraph("• 인터넷 연결 상태를 확인하세요", bullet_style))
story.append(Paragraph("• 챗봇 창을 닫았다가 다시 열어보세요", bullet_style))
story.append(Paragraph("• 질문이 너무 길거나 복잡한 경우 짧게 나눠서 질문하세요", bullet_style))
story.append(Paragraph("• 일시적인 서버 문제일 수 있으니 잠시 후 다시 시도하세요", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("7.5 CSV 다운로드가 안 되는 경우", heading2_style))
story.append(Paragraph("증상: CSV 다운로드 버튼이 작동하지 않습니다.", body_style))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("해결 방법:", body_style))
story.append(Paragraph("• 브라우저의 팝업 차단 설정을 확인하세요", bullet_style))
story.append(Paragraph("• 다운로드 폴더 권한을 확인하세요", bullet_style))
story.append(Paragraph("• 다른 브라우저에서 시도해보세요", bullet_style))
story.append(Paragraph("• 예측 결과를 복사하여 엑셀에 직접 붙여넣으세요", bullet_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("7.6 화면 레이아웃이 깨지는 경우", heading2_style))
story.append(Paragraph("증상: 메뉴나 버튼이 겹치거나 이상한 위치에 표시됩니다.", body_style))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("해결 방법:", body_style))
story.append(Paragraph("• 브라우저 확대/축소를 100%로 설정하세요", bullet_style))
story.append(Paragraph("• 브라우저 창 크기를 조정해보세요", bullet_style))
story.append(Paragraph("• F5 키를 눌러 페이지를 새로고침하세요", bullet_style))
story.append(Paragraph("• PC의 경우 화면 해상도를 1920x1080 이상으로 설정하세요", bullet_style))
story.append(PageBreak())

# 8. 부록
story.append(Paragraph("8. 부록", heading1_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("8.1 용어 설명", heading2_style))

terms = [
    ("낙찰고가", "해당 거래에서 가장 높게 낙찰된 가격"),
    ("낙찰저가", "해당 거래에서 가장 낮게 낙찰된 가격"),
    ("평균가", "낙찰고가와 낙찰저가의 평균값"),
    ("파일어종", "데이터에서 분류되는 대분류 어종명 (예: 갈치, 광어 등)"),
    ("어종", "세부 품종 및 상태가 포함된 어종명 (예: (활)광어, (냉)갈치 등)"),
    ("산지", "수산물이 생산되거나 거래되는 지역"),
    ("규격_등급", "수산물의 크기와 품질 등급"),
    ("포장_분류", "수산물의 포장 형태 (상자, 박스, 망 등)"),
    ("신뢰구간", "예측값이 위치할 것으로 예상되는 범위"),
    ("상관계수", "두 변수 간의 관계 강도를 나타내는 지표 (-1 ~ 1)"),
    ("변동률", "가격 변화의 비율 (%)"),
    ("RAG", "검색 증강 생성 기술로, 데이터를 검색하여 답변하는 AI 방식"),
    ("Prophet", "Facebook이 개발한 시계열 예측 알고리즘"),
    ("Random Forest", "여러 의사결정나무를 결합한 머신러닝 알고리즘")
]

for term, definition in terms:
    story.append(Paragraph(f"<b>{term}</b>", 
        ParagraphStyle('term', parent=body_style, fontSize=11, 
                    fontName=font_name, leftIndent=10)))
    story.append(Paragraph(definition, 
        ParagraphStyle('def', parent=body_style, fontSize=10, 
                    leftIndent=30, spaceAfter=5)))

story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("8.2 데이터 컬럼 설명", heading2_style))

columns = [
    ("date", "거래 날짜 (YYYY-MM-DD 형식)"),
    ("파일어종", "대분류 어종명"),
    ("어종", "세부 품종 및 상태"),
    ("산지", "생산지 또는 거래지"),
    ("낙찰고가", "최고 낙찰 가격 (원)"),
    ("낙찰저가", "최저 낙찰 가격 (원)"),
    ("평균가", "평균 낙찰 가격 (원)"),
    ("수량", "거래 수량"),
    ("중량", "거래 중량 (kg)"),
    ("기온 평균", "해당 산지의 평균 기온 (°C)"),
    ("수온 평균", "해당 산지의 평균 수온 (°C)"),
    ("풍속 평균", "해당 산지의 평균 풍속 (m/s)")
]

col_table = Table(columns, colWidths=[4*cm, 12*cm])
col_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f7fa')),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
]))
story.append(col_table)
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("8.3 시스템 권장 사양", heading2_style))

spec_data = [
    ['구분', '권장 사양'],
    ['운영체제', 'Windows 10 이상, macOS 10.14 이상'],
    ['브라우저', 'Chrome 90 이상, Edge 90 이상, Firefox 88 이상'],
    ['화면 해상도', '1920 x 1080 이상'],
    ['인터넷 속도', '10 Mbps 이상'],
    ['RAM', '4GB 이상']
]

spec_table = Table(spec_data, colWidths=[4*cm, 12*cm])
spec_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f5f7fa')),
    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
]))
story.append(spec_table)
story.append(PageBreak())

# 9. 연락처 및 지원
story.append(Paragraph("9. 연락처 및 지원", heading1_style))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("9.1 고객 지원", heading2_style))
story.append(Paragraph("호갱제로는 사용자 여러분의 성공적인 수산물 거래를 위해 다양한 지원을 제공합니다.", body_style))
story.append(Spacer(1, 0.3*cm))

contact_data = [
    ['지원 항목', '연락처 / 방법'],
    ['기술 지원', 'support@hogaengzero.com'],
    ['영업 문의', 'sales@hogaengzero.com'],
    ['제휴 문의', 'partnership@hogaengzero.com'],
    ['웹사이트', 'www.hogaengzero.com'],
    ['고객센터', '1588-XXXX (평일 09:00~18:00)'],
    ['24시간 챗봇', '시스템 우측 하단 챗봇 버튼']
]

contact_table = Table(contact_data, colWidths=[5*cm, 11*cm])
contact_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f5f7fa')),
    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
]))
story.append(contact_table)
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("9.2 업데이트 및 공지사항", heading2_style))
story.append(Paragraph("• 시스템 업데이트 및 신규 기능은 웹사이트와 이메일을 통해 공지됩니다", bullet_style))
story.append(Paragraph("• 정기 점검은 매주 일요일 새벽 2시~4시에 진행됩니다", bullet_style))
story.append(Paragraph("• 긴급 점검 시에는 팝업으로 사전 안내됩니다", bullet_style))
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph("9.3 피드백 및 개선 제안", heading2_style))
story.append(Paragraph(
    "호갱제로는 사용자 여러분의 의견을 소중히 생각합니다. "
    "시스템 개선 아이디어나 불편 사항이 있으시면 언제든지 feedback@hogaengzero.com으로 의견을 보내주세요. "
    "여러분의 피드백은 더 나은 서비스를 만드는 데 큰 도움이 됩니다.",
    body_style
))
story.append(Spacer(1, 1*cm))

# 맺음말
story.append(Paragraph(
    "호갱제로와 함께 투명하고 합리적인 수산물 거래를 경험하세요. "
    "본 사용설명서가 시스템 활용에 도움이 되기를 바랍니다. "
    "감사합니다.",
    ParagraphStyle('closing', parent=body_style, alignment=TA_CENTER, 
                fontSize=12, textColor=colors.HexColor('#667eea'), 
                fontName=font_name, spaceAfter=30)
))

story.append(Spacer(1, 1*cm))

# 로고 및 저작권
story.append(Paragraph("호갱제로", 
    ParagraphStyle('logo', parent=title_style, fontSize=20, alignment=TA_CENTER)))
story.append(Paragraph(
    "© 2025 호갱제로. All Rights Reserved.",
    ParagraphStyle('copyright', parent=body_style, alignment=TA_CENTER, 
                fontSize=9, textColor=colors.grey)
))

# PDF 생성
try:
    doc.build(story)
    print(f"✅ PDF 생성 완료: {pdf_filename}")
    print(f"📄 파일 위치: {os.path.abspath(pdf_filename)}")
except Exception as e:
    print(f"❌ PDF 생성 실패: {e}")
    