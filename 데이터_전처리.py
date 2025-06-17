import pandas as pd
import os

###################################################################################
# ✔ 전처리 함수 영역 (파생 변수 포함)
###################################################################################
def pm10_grade(value):
    if value <= 30: return '좋음'
    elif value <= 80: return '보통'
    elif value <= 150: return '나쁨'
    else: return '매우나쁨'

def pm25_grade(value):
    if value <= 15: return '좋음'
    elif value <= 35: return '보통'
    elif value <= 75: return '나쁨'
    else: return '매우나쁨'

def humidity_level(humidity):
    if humidity < 40: return '낮음'
    elif humidity <= 70: return '보통'
    else: return '높음'

def get_season(month):
    if month in [3, 4, 5]: return '봄'
    elif month in [6, 7, 8]: return '여름'
    elif month in [9, 10, 11]: return '가을'
    else: return '겨울'

def preprocess_individual_dust(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')

    # 1. 결측치 제거
    df = df.dropna(subset=['측정일시', 'PM10', 'PM25'])

    # 2. 이상치 제거: 음수값 제거
    for col in ['PM10', 'PM25', 'SO2', 'CO', 'O3', 'NO2']:
        if col in df.columns: df = df[df[col] >= 0]

    # 3. 날짜 형식으로 변환
    df['측정일시'] = pd.to_datetime(df['측정일시'], errors='coerce')
    df = df.dropna(subset=['측정일시'])

    # 4. 중복 제거
    df = df.drop_duplicates()

    # 5. 불필요한 칼럼 제거
    drop_cols = ['지역', '측정소코드', '주소']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # 6. 파생 변수 추가
    df['PM10 등급'] = df['PM10'].apply(pm10_grade)
    df['PM25 등급'] = df['PM25'].apply(pm25_grade)

    return df

def preprocess_weather(file_path):
    df = pd.read_csv(file_path, encoding='cp949')

    cols_needed = [col for col in ['일시', '기온(°C)', '습도(%)', '풍속(m/s)'] if col in df.columns]
    df = df.dropna(subset=cols_needed)

    for col in ['기온(°C)', '습도(%)', '풍속(m/s)', '시정(10m)']:
        if col in df.columns: df = df[df[col] >= 0]

    df['일시'] = pd.to_datetime(df['일시'], errors='coerce')
    df = df.dropna(subset=['일시'])
    df = df.drop_duplicates()

    drop_cols = ['지점', '풍향(16방위)', '운형(운형약어)', '지면상태(지면상태코드)', '현상번호(국내식)', '30cm 지중온도(°C)']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # 파생 변수 추가
    df['체감온도'] = 13.12 + 0.6215 * df['기온(°C)'] - 11.37 * df['풍속(m/s)']**0.16 + 0.3965 * df['기온(°C)'] * df['풍속(m/s)']**0.16
    df['습도범주'] = df['습도(%)'].apply(humidity_level)

    return df

def preprocess_sales(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')

    df = df.dropna(subset=['Calendar Day일 2', 'Sales (Bag)', 'Sales Amt'])
    df = df[(df['Sales (Bag)'] >= 0) & (df['Sales Amt'] >= 0)]

    df['Calendar Day일 2'] = pd.to_datetime(df['Calendar Day일 2'], errors='coerce')
    df = df.dropna(subset=['Calendar Day일 2'])
    df = df.drop_duplicates()

    drop_cols = ['CUSTOMER NAME', 'UPC', '지점', 'SUB-CTG', '박스입수', '수량(CS)', '가격', '지역', '구군']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # 파생 변수 추가
    df['계절'] = df['Calendar Day일 2'].dt.month.apply(get_season)
    df['할인여부'] = df['금액'] < (df['Sales (Bag)'] * df['Unit Price'])

    return df


###################################################################################
# ✔ 대상 파일 영역
###################################################################################
dust_files = [
    "1701Q_dust.csv", "1702Q_dust.csv", "1703Q_dust.csv", "1704Q_dust.csv",
    "1801Q_dust.csv", "1802Q_dust.csv", "1803Q_dust.csv"
]
weather_files = [
    "SURFACE_air_pollution_2017.csv",
    "SURFACE_air_pollution_2018.csv"
]
sales_files = [
    "20190509_mask_POS.csv"
]

###################################################################################
# ✔ 전처리 결과 저장 영역
###################################################################################
dust_dataframes = {}
weather_dataframes = {}
sales_dataframes = {}

###################################################################################
# ✔ 실행 루프 영역
###################################################################################
def push_preprocessed(file, preprocess_func, dataframe):
    cleaned = preprocess_func("./data/" + file)
    quarter = file.replace(".csv", "")
    dataframe[quarter] = cleaned
    print(f"[완료] {quarter} 전처리 완료. 행 수: {len(cleaned)}")

for file in dust_files:
    push_preprocessed(file, preprocess_individual_dust, dust_dataframes)
for file in weather_files:
    push_preprocessed(file, preprocess_weather, weather_dataframes)
for file in sales_files:
    push_preprocessed(file, preprocess_sales, sales_dataframes)

###################################################################################
# ✔ 미리보기 영역
###################################################################################
print("\n[미리보기]")
print("\n[2017년 1분기 미세먼지 데이터]")
print(dust_dataframes['1701Q_dust'].head(3))
print("\n[2017년 대기오염 데이터]")
print(weather_dataframes['SURFACE_air_pollution_2017'].head(3))
print("\n[2017년 ~ 2019년 1분기 마스크 판매량 데이터]")
print(sales_dataframes['20190509_mask_POS'].head(3))

###################################################################################
# ✔ 전처리된 데이터 저장 영역
###################################################################################
output_dir = "./cleaned_data"
os.makedirs(output_dir, exist_ok=True)

def save_cleaned_dataframes(dataframes_dict, prefix):
    for name, df in dataframes_dict.items():
        save_path = os.path.join(output_dir, f"{prefix}_{name}.csv")
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"[저장 완료] {save_path}")

save_cleaned_dataframes(dust_dataframes, "dust") # 미세먼지 측정 데이터 저장
save_cleaned_dataframes(weather_dataframes, "weather") # 기상 데이터 저장
save_cleaned_dataframes(sales_dataframes, "sales") # 마스크 판매 데이터 저장