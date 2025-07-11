import pandas as pd
import glob

# 1. 파일 경로 설정
path = './real_estate_data/'  # 연도별 CSV 파일 경로
files = glob.glob(path + '*.csv')

# 2. 결과 리스트 초기화
df_list = []

# 3. 파일 반복 처리
for file in files:
    try:
        # 파일 불러오기
        df = pd.read_csv(file, encoding='cp949', skiprows=15)

        # 주요 컬럼만 선택
        df_cleaned = df[['시군구', '전용면적(㎡)', '거래금액(만원)', '계약년월']].copy()

        # 거래금액 쉼표 제거 후 정수형 변환
        df_cleaned['거래금액(만원)'] = df_cleaned['거래금액(만원)'].str.replace(",", "").astype(int)

        # 연, 월 분리
        df_cleaned['년'] = df_cleaned['계약년월'].astype(str).str[:4].astype(int)
        df_cleaned['월'] = df_cleaned['계약년월'].astype(str).str[4:].astype(int)

        # 읍면동 추출 (예: "제주시 연동" → "연동")
        df_cleaned['읍면동'] = df_cleaned['시군구']

        # 평당가격 계산
        df_cleaned['평당가격'] = df_cleaned['거래금액(만원)'] / (df_cleaned['전용면적(㎡)'] / 3.3)

        df_list.append(df_cleaned)

    except Exception as e:
        print(f"⚠️ {file} 처리 중 오류 발생:", e)

# 4. 병합
df_total = pd.concat(df_list, ignore_index=True)

# 5. 저장
df_total.to_csv("jeju_real_estate.csv", index=False, encoding='utf-8-sig')
