import matplotlib.pyplot as plt
import pandas as pd
import glob

plt.rc('font', family='Malgun Gothic') # 한글 폰트 설정 (Windows: 맑은 고딕, macOS: AppleGothic)
plt.rcParams['axes.unicode_minus'] = False # 마이너스 깨짐 방지

# 📁 데이터 불러오기
dust_files = sorted(glob.glob("./data/*_dust.csv"))  # data 폴더 기준
dust_dataframes = [pd.read_csv(file, encoding='utf-8') for file in dust_files]
df_dust = pd.concat(dust_dataframes, ignore_index=True)

df_dust['측정일시'] = df_dust['측정일시'].astype(str).str[:10]
df_dust['측정일시'] = pd.to_datetime(df_dust['측정일시'], format='%Y%m%d%H', errors='coerce')
df_dust = df_dust.dropna(subset=['측정일시'])
df_dust['연도'] = df_dust['측정일시'].dt.year
df_dust['월'] = df_dust['측정일시'].dt.month
monthly_dust = df_dust[df_dust['연도'].isin([2017, 2018])].groupby(['연도', '월'])[
    ['PM10', 'PM25', 'SO2', 'CO', 'O3', 'NO2']].mean().reset_index()

# 😷 마스크 판매 데이터
mask_sales = pd.read_csv("./data/20190509_mask_POS.csv", encoding='utf-8')
mask_sales['날짜'] = pd.to_datetime(mask_sales['Calendar Day일 2'], errors='coerce')
mask_sales = mask_sales.dropna(subset=['날짜'])
mask_sales['연도'] = mask_sales['날짜'].dt.year
mask_sales['월'] = mask_sales['날짜'].dt.month
monthly_sales = mask_sales[mask_sales['연도'].isin([2017, 2018])].groupby(['연도', '월'])[
    'Sales (Bag)'].sum().reset_index(name='판매량')

# 1️⃣ PM10 / PM2.5 꺾은선 그래프
plt.figure(figsize=(10, 5))
for year in [2017, 2018]:
    subset = monthly_dust[monthly_dust['연도'] == year]
    plt.plot(subset['월'], subset['PM10'], marker='o', label=f'{year} PM10')
    plt.plot(subset['월'], subset['PM25'], marker='s', label=f'{year} PM2.5')
plt.title('2017년 vs 2018년 월별 미세먼지 농도')
plt.xlabel('월')
plt.ylabel('농도 (㎍/㎥)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 2️⃣ 마스크 판매량 막대 그래프
plt.figure(figsize=(10, 5))
bar_width = 0.35
months = sorted(monthly_sales['월'].unique())
sales_2017 = monthly_sales[monthly_sales['연도'] == 2017].set_index('월').reindex(months)['판매량']
sales_2018 = monthly_sales[monthly_sales['연도'] == 2018].set_index('월').reindex(months)['판매량']
plt.bar([m - bar_width/2 for m in months], sales_2017, width=bar_width, label='2017')
plt.bar([m + bar_width/2 for m in months], sales_2018, width=bar_width, label='2018')
plt.title('2017년 vs 2018년 월별 마스크 판매량')
plt.xlabel('월')
plt.ylabel('판매량')
plt.xticks(months)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 3️⃣ 오염물질 4종 (SO2, CO, O3, NO2) 서브플롯 그래프
pollutants = ['SO2', 'CO', 'O3', 'NO2']
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
axs = axs.flatten()
for i, gas in enumerate(pollutants):
    ax = axs[i]
    for year in [2017, 2018]:
        subset = monthly_dust[monthly_dust['연도'] == year]
        offset = 0.2 if year == 2018 else -0.2
        ax.bar([x + offset for x in subset['월']], subset[gas], width=0.4, label=f'{year}')
    ax.set_title(f'{gas} 월별 평균 농도')
    ax.set_xlabel('월')
    ax.set_ylabel('농도')
    ax.set_xticks(months)
    ax.legend()
    ax.grid(True)
plt.suptitle('2017년 vs 2018년 월별 대기 오염물질 (SO2, CO, O3, NO2)', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()