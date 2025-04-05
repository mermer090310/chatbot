import streamlit as st
from openai import OpenAI
import pandas as pd

# Show title and description.
st.title("🏃‍♂️ 러닝 기록 챗봇")
st.write(
    "당신이 달린 날짜를 입력해주세요! "
    "궁금한 점이 있으면 언제든 물어보세요. "
    "이 앱을 사용하려면 OpenAI API 키가 필요합니다. [여기](https://platform.openai.com/account/api-keys)에서 얻을 수 있어요."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "당신은 러닝 기록 챗봇입니다. 사용자에게 러닝한 날짜, 거리, 시간을 각각의 셀로 입력 받아 그 값을 표에 기록해주세요. 시간의 흐름에 따라 기록을 정리하세요." }
        ]

    # 러닝 기록 입력을 위한 표 생성
    st.subheader("러닝 기록 입력")
    if "running_df" not in st.session_state:
        st.session_state.running_df = pd.DataFrame(
            {"날짜": ["", "", ""], "거리(km)": ["", "", ""], "시간(분)": ["", "", ""]}
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

    # "기록 분석하기" 버튼 추가
    if st.button("기록 분석하기"):
        # 표에서 입력된 기록을 문자열로 변환
        running_list = [
            f"{row['날짜']}에 {row['거리(km)']}km를 {row['시간(분)']}분 동안 달렸어"
            for _, row in edited_df.iterrows()
            if row["날짜"] and row["거리(km)"] and row["시간(분)"]  # 빈 값 제외
        ]
        if running_list:
            prompt = f"내 러닝 기록이야: {', '.join(running_list)}. 이걸 분석해서 조언해줄래?"
        else:
            prompt = "러닝 기록을 입력해주세요!"

        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI API로 응답 생성
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # 응답 스트리밍 및 저장
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 기존 채팅 메시지 표시
    st.subheader("대화 기록")
    for message in st.session_state.messages:
        if message["role"] != "system":  # 시스템 메시지는 표시하지 않음
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 추가 질문 입력 필드
    if prompt := st.chat_input("오늘 날짜를 입력하세요"):

        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI API로 응답 생성
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # 응답 스트리밍 및 저장
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
