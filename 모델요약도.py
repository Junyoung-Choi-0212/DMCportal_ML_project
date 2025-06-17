import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ✅ 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows용. Mac은 'AppleGothic', Linux는 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 🔧 기본 설정
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')
ax.set_xlim(0, 11)
ax.set_ylim(1, 6)

# 📦 박스 그리기 함수
def draw_box(x, y, text, color, width=2, height=1, zorder=1):
    ax.add_patch(FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.03",
        edgecolor='black',
        facecolor=color,
        linewidth=1.5,
        zorder=zorder
    ))
    if text:
        ax.text(x + width / 2, y + height / 2, text,
                va='center', ha='center', fontsize=11, zorder=zorder + 1)

# 📂 상단 그룹 박스 정보
group_x = 0.3
group_y = 4.3
group_width = 10.0
group_height = 1.4

# 🟥 그룹 박스 (배경만)
draw_box(group_x, group_y, "", "#FFECEC", width=group_width, height=group_height, zorder=0)

# 🏷️ 그룹 박스 제목 텍스트 (따로 출력)
ax.text(group_x + group_width / 2, group_y + group_height + 0.1,
        "모델 학습 및 예측 흐름", ha='center', va='bottom', fontsize=12, fontweight='bold')

# ⬆️ 상단 박스 4개
model_flow = [
    ("대기오염/판매 데이터", 0.5, 4.5),
    ("전처리 및\n피처 생성", 3.0, 4.5),
    ("예측 모델 학습", 5.5, 4.5),
    ("판매량 예측 결과", 8.0, 4.5),
]
for text, x, y in model_flow:
    draw_box(x, y, text, "#FFE0E0")

# ⬇️ 하단 박스 3개
user_flow = [
    ("마케팅 전략 수립", 1.5, 2.0),
    ("분석 웹앱 대시보드", 4.5, 2.0),
    ("프로모션 실행\n의사결정", 7.5, 2.0),
]
for text, x, y in user_flow:
    draw_box(x, y, text, "#E0F0FF")

# ➡️ 화살표 그리기 함수
def draw_arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=1.8, color='gray'))

# 🔁 상단 흐름 연결
for i in range(len(model_flow) - 1):
    draw_arrow(model_flow[i][1] + 2, model_flow[i][2] + 0.5,
               model_flow[i + 1][1], model_flow[i + 1][2] + 0.5)

# 🔁 하단 흐름 연결
for i in range(len(user_flow) - 1):
    draw_arrow(user_flow[i][1] + 2, user_flow[i][2] + 0.5,
               user_flow[i + 1][1], user_flow[i + 1][2] + 0.5)

# 🔽 상단 그룹 중앙 → 하단 중앙 화살표
x_center = group_x + group_width / 2
y_top = group_y
y_bottom = user_flow[1][2] + 1.0
draw_arrow(x_center, y_top, user_flow[1][1] + 1, y_bottom)

plt.tight_layout()
plt.show()