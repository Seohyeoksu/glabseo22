import os
from openai import OpenAI
import streamlit as st
from gtts import gTTS
import os
import base64

# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 초기 대본 정의 (문장 단위로 나누어 리스트로 저장)
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

# 세션 상태 초기화
if 'current_line' not in st.session_state:
    st.session_state.current_line = 0
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# 제목 설정
st.title("Charlotte's Web Interactive Learning")

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("current_line.mp3")
    
    with open("current_line.mp3", "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    audio_player = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}">'
    st.markdown(audio_player, unsafe_allow_html=True)
    
    os.remove("current_line.mp3")

# GPT-4를 사용한 대화 생성 함수
def generate_response(prompt):
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    rchat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI tutor helping a student learn English through the story of Charlotte's Web. Provide explanations, answer questions, and engage in dialogue about the story, characters, and language used. Keep your responses appropriate for young learners."},
            *st.session_state.conversation_history
        ]
    )
    
    ai_response = response.choices[0].message['content'].strip()
    st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
    return ai_response

# 전체 대본 표시 및 각 문장에 대한 듣기 버튼 추가
st.write("Full Script:")
for i, line in enumerate(initial_script):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(line)
    with col2:
        if st.button(f"Listen", key=f"listen_{i}"):
            text_to_speech(line)

# 순차적 듣기 기능
st.write("Sequential Listening:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Previous line") and st.session_state.current_line > 0:
        st.session_state.current_line -= 1

with col2:
    if st.button("Listen to current line"):
        text_to_speech(initial_script[st.session_state.current_line])

with col3:
    if st.button("Next line") and st.session_state.current_line < len(initial_script) - 1:
        st.session_state.current_line += 1

# 현재 문장 표시
st.write(f"Current line: {initial_script[st.session_state.current_line]}")

# 대화형 학습 섹션
st.write("Interactive Learning:")
user_input = st.text_input("Ask a question about the story, characters, or language:")
if st.button("Submit"):
    ai_response = generate_response(user_input)
    st.write("AI Tutor:", ai_response)
    if st.button("Listen to AI response"):
        text_to_speech(ai_response)

# 대화 기록 표시
st.write("Conversation History:")
for message in st.session_state.conversation_history:
    st.write(f"{message['role'].capitalize()}: {message['content']}")
