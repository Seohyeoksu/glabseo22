import os
import openai
import streamlit as st
from difflib import SequenceMatcher

openai.api_key = st.secrets['API_KEY']

initial_script = [
    "Narrator: It's a beautiful fall morning on the farm.",
    "Narrator: The leaves are turning yellow and red.",
    "Narrator: Fern comes to visit Wilbur, her favorite pig.",
    "Fern: Good morning, Wilbur! How are you today?",
    "Wilbur: Oh, Fern! I'm so happy to see you. I was feeling a little lonely.",
    "Fern: Don't be lonely, Wilbur. You have so many friends here on the farm!",
    "Charlotte: Good morning, Fern. You're right, Wilbur has many friends, including me.",
    "Wilbur: Charlotte! I'm so glad you're here. Fern, isn't Charlotte amazing? She can make the most beautiful webs."
]

if 'current_line' not in st.session_state:
    st.session_state.current_line = 0
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

st.markdown("""
<style>
    .main {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        background-color: #e6f3ff;
        border-radius: 5px;
    }
    h1 {
        color: #2E8B57;
        text-align: center;
    }
    h2 {
        color: #4682B4;
    }
    .script-line {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🕷️ 샬롯의 거미줄 인터랙티브 학습 🐷")

def text_to_speech(text):
    from gtts import gTTS
    from io import BytesIO

    tts = gTTS(text=text, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    st.audio(audio_bytes.read(), format='audio/mp3')

def generate_response(prompt):
    st.session_state.conversation_history.append({"role": "user", "content": prompt})

    try:
        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI tutor helping a student learn English through the story of Charlotte's Web. Provide explanations, answer questions, and engage in dialogue about the story, characters, and language used. Keep your responses appropriate for young learners."},
                *st.session_state.conversation_history
            ]
        )

        ai_response = chat_completion.choices[0].message.content.strip()
        st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        st.error(f"에러가 발생했습니다: {str(e)}")
        return "죄송합니다. 오류가 발생했습니다. 다시 시도해주세요."

st.sidebar.header("전체 대본")
for i, line in enumerate(initial_script):
    st.sidebar.markdown(f'<div class="script-line">{line}</div>', unsafe_allow_html=True)
    if st.sidebar.button(f"🔊 듣기", key=f"listen_{i}"):
        text_to_speech(line)

st.header("🎧 순차적 듣기")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⏮️ 이전 줄") and st.session_state.current_line > 0:
        st.session_state.current_line -= 1

with col2:
    if st.button("▶️ 현재 줄 듣기"):
        text_to_speech(initial_script[st.session_state.current_line])

with col3:
    if st.button("⏭️ 다음 줄") and st.session_state.current_line < len(initial_script) - 1:
        st.session_state.current_line += 1

st.info(f"현재 줄: {initial_script[st.session_state.current_line]}")

st.header("💬 인터랙티브 학습")
user_input = st.text_input("스토리, 등장인물 또는 언어에 대해 질문하세요:")

if st.button("🚀 제출") and user_input:
    with st.spinner("AI 튜터가 생각 중입니다..."):
        ai_response = generate_response(user_input)
    st.success("AI 튜터: " + ai_response)
    if st.button("🔊 AI 응답 듣기"):
        text_to_speech(ai_response)

st.header("📜 대화 기록")
for message in st.session_state.conversation_history:
    if message['role'] == 'user':
        st.markdown(f"**사용자:** {message['content']}")
    else:
        st.markdown(f"**AI 튜터:** {message['content']}")
