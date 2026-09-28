import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------
# 기본 설정
# ---------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# ---------------------------------------
# 데이터 불러오기
# ---------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 실제 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# =======================================
# 그래프 1
# =======================================
st.header("📈 그래프 1. 영화별 날짜에 따른 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()
movie_df = movie_df.sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie}의 날짜별 일관객"
)

fig1.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객(명)",
    hovermode="x"
)

fig1.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: 선택한 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)


# =======================================
# 그래프 2
# =======================================
st.header("📊 그래프 2. 일관객 합계 상위 5편")

movie_total = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
)

top5_movies = movie_total.head(5)["영화명"].tolist()

top5_df = df[df["영화명"].isin(top5_movies)].copy()
top5_df = top5_df.sort_values(["날짜", "영화명"])

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객"
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객(명)",
    hovermode="x unified",
    legend_title="영화명"
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}<br>"
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: 전체 기간 동안 일관객 합계가 큰 5편의 날짜별 관객 변화를 비교할 수 있습니다."
)

st.subheader("🏆 일관객 합계 상위 5편")

top5_table = movie_total.head(5).copy()
top5_table["일관객"] = top5_table["일관객"].map(
    lambda x: f"{int(x):,}명"
)

st.dataframe(
    top5_table,
    hide_index=True,
    use_container_width=True
)


# =======================================
# 그래프 3
# =======================================
st.header("🌊 그래프 3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("일관객", ascending=False)
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계"
)

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)",
    hovermode="x"
)

fig3.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,}명"
        "<extra></extra>"
    )
)

for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"{row['날짜'].strftime('%Y-%m-%d')}"
            f"<br>{int(row['일관객']):,}명"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50
    )

st.plotly_chart(fig3, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: 날짜별로 당시 10위권 영화 전체의 일관객 규모가 어떻게 변했는지 확인할 수 있습니다."
)

st.subheader("🔥 10위권 일관객 합계가 가장 컸던 3일")

top3_display = top3_days.copy()

top3_display["날짜"] = top3_display["날짜"].dt.strftime("%Y-%m-%d")

top3_display["일관객"] = top3_display["일관객"].map(
    lambda x: f"{int(x):,}명"
)

top3_display = top3_display.rename(
    columns={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

st.dataframe(
    top3_display,
    hide_index=True,
    use_container_width=True
)


# =======================================
# 그래프 4
# =======================================
st.header("🏆 그래프 4. 기간 전체 일관객 TOP 10")

movie_stats = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        **{"10위권에_든_날수": ("날짜", "nunique")}
    )
    .reset_index()
)

top10_movies = (
    movie_stats
    .sort_values("일관객합계", ascending=False)
    .head(10)
    .sort_values("일관객합계", ascending=True)
)

fig4 = px.bar(
    top10_movies,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="이 기간 일관객 합계 TOP 10",
    text="일관객합계"
)

fig4.update_layout(
    xaxis_title="기간 전체 일관객 합계(명)",
    yaxis_title="영화명",
    hovermode="closest"
)

fig4.update_traces(
    texttemplate="%{text:,}명",
    textposition="outside",
    customdata=top10_movies[["10위권에_든_날수"]].values,
    hovertemplate=(
        "영화: %{y}<br>"
        "기간 전체 일관객: %{x:,}명<br>"
        "10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    )
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: 이 기간 동안 10위권에 등장한 영화들의 전체 일관객 규모를 비교할 수 있으며, 마우스를 올리면 각 영화가 10위권에 든 날수도 확인할 수 있습니다."
)


# =======================================
# 그래프 5
# =======================================
st.header("🔥 그래프 5. 월 × 요일별 일관객 합계")

# ---------------------------------------
# 날짜에서 월과 요일 추출
# ---------------------------------------
heatmap_df = df.copy()

heatmap_df["월"] = heatmap_df["날짜"].dt.month

# 한국어 요일 이름으로 변환
weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek.map(weekday_map)

# 요일 순서 고정
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

# 월 × 요일별 일관객 합계
monthly_weekday_total = (
    heatmap_df
    .groupby(["월", "요일"], as_index=False)["일관객"]
    .sum()
)

# 피벗 테이블로 변환
heatmap_pivot = (
    monthly_weekday_total
    .pivot(
        index="월",
        columns="요일",
        values="일관객"
    )
    .reindex(columns=weekday_order)
)

# 월 순서 1월 → 12월
heatmap_pivot = heatmap_pivot.sort_index()

# ---------------------------------------
# 히트맵
# ---------------------------------------
fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_order,
    y=[f"{month}월" for month in heatmap_pivot.index],
    aspect="auto",
    text_auto=".0f",
    color_continuous_scale="Blues",
    title="월 × 요일별 10위권 일관객 합계"
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    coloraxis_colorbar_title="일관객"
)

fig5.update_traces(
    hovertemplate=(
        "%{y} %{x}<br>"
        "일관객 합계: %{z:,}명"
        "<extra></extra>"
    )
)

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: 어떤 월과 요일에 10위권 영화의 일관객 합계가 많았는지 한눈에 비교할 수 있습니다. 색이 진할수록 일관객 합계가 많습니다."
)


# =======================================
# 그래프 6
# =======================================
st.header("📌 그래프 6. 추가 예정")

st.write("다음 그래프를 이곳에 추가할 수 있습니다.")

