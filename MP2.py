import pandas as pd
import folium
import requests

# 1. CSV 불러오기 및 '읍면동' 전처리 (리 제거 포함)
df = pd.read_csv("jeju_real_estate.csv", encoding='utf-8-sig')
df = df.dropna(subset=['읍면동', '평당가격'])

# 공백 제거하고, '리' 제거, 읍/면/동 단위만 추출
df['읍면동'] = df['읍면동'].str.extract(r'([가-힣]+[읍면동])')[0]


# 2. 법정동(읍면동) → 행정동 매핑 딕셔너리
legal_to_admin = {
    # 일도동
    '일도일동': '일도1동',
    '일도이동': '일도2동',
    '일도1동': '일도1동',
    '일도2동': '일도2동',

    # 이도동
    '이도일동': '이도1동',
    '이도이동': '이도2동',
    '이도1동': '이도1동',
    '이도2동': '이도2동',
    '도남동': '이도2동',

    # 삼도동
    '삼도일동': '삼도1동',
    '삼도이동': '삼도2동',
    '삼도1동': '삼도1동',
    '삼도2동': '삼도2동',

    # 삼양동
    '삼양일동': '삼양동',
    '삼양이동': '삼양동',
    '삼양삼동': '삼양동',
    '삼양1동': '삼양동',
    '삼양2동': '삼양동',
    '삼양3동': '삼양동',
    '도련동': '삼양동',
    '도련일동': '삼양동',
    '도련이동': '삼양동',

    # 용담동
    '용담일동': '용담1동',
    '용담이동': '용담2동',
    '용담삼동': '용담2동',
    '용담1동': '용담1동',
    '용담2동': '용담2동',
    '용담3동': '용담2동',

    # 오라동
    '오라일동': '오라동',
    '오라이동': '오라동',
    '오라삼동': '오라동',
    '오라1동': '오라동',
    '오라2동': '오라동',
    '오라3동': '오라동',

    # 아라동
    '아라일동': '아라동',
    '아라이동': '아라동',
    '아라1동': '아라동',
    '아라2동': '아라동',
    '영평동': '아라동',
    '월평동': '아라동',
    '오등동': '아라동',

    # 외도동
    '외도일동': '외도동',
    '외도이동': '외도동',
    '외도1동': '외도동',
    '외도2동': '외도동',
    '도평동': '외도동',
    '내도동': '외도동',

    # 이호동
    '이호일동': '이호동',
    '이호이동': '이호동',
    '이호1동': '이호동',
    '이호2동': '이호동',

    # 도두동
    '도두일동': '도두동',
    '도두이동': '도두동',
    '도두1동': '도두동',
    '도두2동': '도두동',
    
    # 대천동
    '강정동': '대천동',
    '도순동': '대천동',
    '영남동': '대천동',
    
    # 화북동
    '화북일동': '화북동',
    '화북이동': '화북동',
    
    # 구좌읍
    '한동': '구좌읍',
    '구좌읍': '구좌읍',
    
    # 봉개동
    '회천동': '봉개동',
    '봉개동': '봉개동',
    '용강동': '봉개동',
    
    # 중문동
    '대포동': '중문동',
    '중문동': '중문동',
    '회수동': '중문동',
    '하원동': '중문동',
    
    # 효돈동
    '신효동': '효돈동',
    '하효동': '효돈동',
    
    # 영천동
    '상효동': '영천동',
    '토평동': '영천동',
    
    # 예래동
    '색달동': '예래동',
    '하예동': '예래동',
    '상예동': '예래동',
    
    # 노형동
    '해안동': '노형동',
    '노형동': '노형동',
    
    # 대륜동
    '법환동': '대륜동',
    '서호동': '대륜동', 
    '호근동': '대륜동',
    
    '건입동': '건입동',
    '천지동': '천지동',
    '서귀동': '정방동',
    '보목동': '송산동',
    '서홍동': '서홍동',
    '동홍동': '동홍동',
    '연동': '연동',
    '안덕면': '안덕면',
    '남원읍': '남원읍',
    '표선면': '표선면',
    '한림읍': '한림읍',
    '성산읍': '성산읍',
    '한경면': '한경면',
    '애월읍': '애월읍',
    '추자면': '추자면',
    '대정읍': '대정읍',
    '우도면': '우도면',
    '조천읍': '조천읍'
}


# 3. 법정동 → 행정동 컬럼 추가
df['행정동'] = df['읍면동'].map(legal_to_admin)

# 4. 매핑 안 된 읍면동 확인 (있으면 직접 매핑 추가 필요)
missing_admin = df[df['행정동'].isna()]['읍면동'].unique()
if len(missing_admin) > 0:
    print("매핑 없는 읍면동:", missing_admin)

# 5. 행정동별 평균 평당가격 계산
grouped_admin = df.groupby('행정동')['평당가격'].mean().reset_index()

# 6. GeoJSON 불러오기 및 제주도 행정동 필터링
geo_url = 'https://raw.githubusercontent.com/vuski/admdongkor/master/ver20220701/HangJeongDong_ver20220701.geojson'
geo_data = requests.get(geo_url).json()

jeju_geo = {'type': 'FeatureCollection', 'features': []}
for feature in geo_data['features']:
    if feature['properties']['sidonm'] == '제주특별자치도':
        adm_nm = feature['properties']['adm_nm'].strip().replace(" ", "")
        adm_nm = adm_nm.replace('제주특별자치도제주시', '')
        adm_nm = adm_nm.replace('제주특별자치도서귀포시', '')
        feature['properties']['adm_nm'] = adm_nm
        jeju_geo['features'].append(feature)

# 7. GeoJSON adm_nm 리스트
geo_names = [f['properties']['adm_nm'] for f in jeju_geo['features']]

# 8. 데이터와 GeoJSON 매칭 확인
csv_names = set(grouped_admin['행정동'])
print("CSV에만 있는 행정동:", csv_names - set(geo_names))
print("GeoJSON에만 있는 행정동:", set(geo_names) - csv_names)

# 9. GeoJSON에 있는 행정동만 필터링
filtered = grouped_admin[grouped_admin['행정동'].isin(geo_names)]

# 10. folium 지도 생성 및 Choropleth 시각화
m = folium.Map(location=[33.49, 126.53], zoom_start=11)

folium.Choropleth(
    geo_data=jeju_geo,
    data=filtered,
    columns=['행정동', '평당가격'],
    key_on='feature.properties.adm_nm',
    fill_color='YlOrRd',
    fill_opacity=0.75,
    line_opacity=0.3,
    legend_name='행정동별 평균 평당가격 (만원)',
    highlight=True
).add_to(m)

# 11. 읍면동명 툴팁 추가 (선택)
folium.GeoJson(
    jeju_geo,
    style_function=lambda feature: {'fillColor': 'transparent', 'color': 'black', 'weight': 0.5},
    tooltip=folium.GeoJsonTooltip(fields=['adm_nm'], labels=False)
).add_to(m)

# 12. 결과 저장
m.save("jeju_price_map_admin.html")
print("✅ 지도 저장 완료: jeju_price_map_admin.html")
