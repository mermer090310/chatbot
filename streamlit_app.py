import streamlit as st
import pandas as pd
import datetime

# Show title and description.
st.title("🏃‍♂️ 러닝 기록 챗봇")
st.write(
    "러닝 기록을 입력하면 일자별로 정리하고, 거리 변화를 그래프로 보여드려요!"
)

# 러닝 기록을 저장할 데이터프레임 초기화
if "running_df" not in st.session_state:
    st.session_state.running_df = pd.DataFrame(
        columns=["날짜", "거리(km)", "시간(분)"]
    )

# 러닝 기록 입력 폼 생성
st.subheader("러닝 기록 입력")
with st.form(key="running_form"):
    date = st.text_input("날짜 (YYYY-MM-DD)", placeholder="예: 2025-04-05")
    distance = st.number_input("거리(km)", min_value=0.0, step=0.1, help="킬로미터 단위, 예: 5.0")
    time = st.number_input("시간(분)", min_value=0, step=1, help="분 단위, 예: 30")
    submit_button = st.form_submit_button(label="기록 추가")

    # 폼 제출 시 데이터 추가
    if submit_button:
        if date and distance > 0 and time > 0:
            try:
                # 날짜 형식 검증
                pd.to_datetime(date)
                # 새로운 기록 추가
                new_record = pd.DataFrame(
                    [[date, distance, time]],
                    columns=["날짜", "거리(km)", "시간(분)"]
                )
                st.session_state.running_df = pd.concat(
                    [st.session_state.running_df, new_record], ignore_index=True
                )
                st.success("기록이 추가되었습니다!")
            except ValueError:
                st.error("날짜 형식이 잘못되었습니다. 'YYYY-MM-DD' 형식으로 입력해주세요. (예: 2025-04-05)")
        else:
            st.warning("모든 값을 입력해주세요. 거리와 시간은 0보다 커야 합니다.")

# 기록 정리 및 그래프 그리기
st.subheader("러닝 기록 정리 및 그래프")
if st.button("기록 보기"):
    df = st.session_state.running_df.copy()
    
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
        st.warning("입력된 기록이 없습니다. 데이터를 입력해주세요.")
