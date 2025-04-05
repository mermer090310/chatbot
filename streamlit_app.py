import streamlit as st
import pandas as pd
import datetime

# Show title and description.
st.title("🏃‍♂️ 러닝 기록 챗봇")
st.write(
    "러닝 기록을 입력하면 일자별로 정리하고, 거리 변화를 그래프로 보여드려요!"
)

# 러닝 기록 입력을 위한 표 생성
st.subheader("러닝 기록 입력")
if "running_df" not in st.session_state:
    st.session_state.running_df = pd.DataFrame(
        {"날짜": ["", "", ""], "거리(km)": [0.0, 0.0, 0.0], "시간(분)": [0, 0, 0]}
    )

# 동적 표 편집기
edited_df = st.data_editor(
    st.session_state.running_df,
    num_rows="dynamic",  # 행 추가/삭제 가능
    column_config={
        "날짜": st.column_config.TextColumn("날짜", help="예: 2025-04-05"),
        "거리(km)": st.column_config.NumberColumn("거리(km)", help="킬로미터 단위, 예: 5.0", min_value=0.0),
        "시간(분)": st.column_config.NumberColumn("시간(분)", help="분 단위, 예: 30", min_value=0)
    },
    key="running_table"
)

# 표 데이터를 세션 상태에 저장
st.session_state.running_df = edited_df

# 기록 정리 및 그래프 그리기
st.subheader("러닝 기록 정리 및 그래프")
if st.button("기록 보기"):
    # 빈 값 제외 및 데이터 정리
    df = edited_df.dropna(subset=["날짜", "거리(km)", "시간(분)"]).copy()
    
    if not df.empty:
        # 날짜 형식을 datetime으로 변환
        try:
            df["날짜"] = pd.to_datetime(df["날짜"])
        except Exception as e:
            st.error("날짜 형식이 잘못되었습니다. 'YYYY-MM-DD' 형식으로 입력해주세요. (예: 2025-04-05)")
            st.stop()

        # 날짜순으로 정렬
        df = df.sort_values(by="날짜")

        # 일자별 기록 표시
        st.write("### 일자별 러닝 기록")
        st.dataframe(df[["날짜", "거리(km)", "시간(분)"]])

        # 일자별 거리 그래프 그리기
        st.write("### 일자별 거리 변화 그래프")
        # 날짜를 인덱스로 설정하고 거리만 추출
        df_for_graph = df.set_index("날짜")["거리(km)"]
        st.line_chart(df_for_graph)

    else:
        st.warning("입력된 기록이 없습니다. 표에 데이터를 입력해주세요.")
