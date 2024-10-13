import os
from openai import OpenAI
import streamlit as st
from gtts import gTTS
import base64
import speech_recognition as sr
from difflib import SequenceMatcher

# OpenAI API 키 설정 (기존 코드와 동일)
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 초기 대본 정의 (기존 코드와 동일)
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

# 세션 상태 초기화 (기존 코드와 동일)
if 'current_line' not in st.session_state:
    st.session_state.current_line = 0
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# 커스텀 CSS 스타일 (기존 코드와 동일)
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

# 제목 설정 (기존 코드와 동일)
st.title("🕷️ Charlotte's Web Interactive Learning 🐷")

# 텍스트를 음성으로 변환하고 재생하는 함수 (기존 코드와 동일)
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("current_line.mp3")
    
    with open("current_line.mp3", "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    audio_player = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}">'
    st.markdown(audio_player, unsafe_allow_html=True)
    
    os.remove("current_line.mp3")

# GPT-4를 사용한 대화 생성 함수 (기존 코드와 동일)
def generate_response(prompt):
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    try:
        chat_completion = client.chat.completions.create(
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
        st.error(f"An error occurred: {str(e)}")
        return "I'm sorry, I encountered an error. Please try again."

# 음성 인식 함수 (수정됨)
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("말씀해 주세요...")
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio, language="en-US")
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError:
        return "Google Speech Recognition 서비스에 접근할 수 없습니다."

# 음성 인식 정확도 평가 함수 (새로 추가)
def evaluate_speech_accuracy(original_text, recognized_text):
    similarity = SequenceMatcher(None, original_text.lower(), recognized_text.lower()).ratio()
    return similarity * 100

# 사이드바에 전체 대본 표시 (기존 코드와 동일)
st.sidebar.header("Full Script")
for i, line in enumerate(initial_script):
    st.sidebar.markdown(f'<div class="script-line">{line}</div>', unsafe_allow_html=True)
    if st.sidebar.button(f"🔊 Listen", key=f"listen_{i}"):
        text_to_speech(line)

# 메인 화면에 순차적 듣기 기능 (기존 코드와 동일)
st.header("🎧 Sequential Listening")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⏮️ Previous line") and st.session_state.current_line > 0:
        st.session_state.current_line -= 1

with col2:
    if st.button("▶️ Listen to current line"):
        text_to_speech(initial_script[st.session_state.current_line])

with col3:
    if st.button("⏭️ Next line") and st.session_state.current_line < len(initial_script) - 1:
        st.session_state.current_line += 1

# 현재 문장 표시 (기존 코드와 동일)
st.info(f"Current line: {initial_script[st.session_state.current_line]}")

# 대화형 학습 섹션 (음성 인식 정확도 평가 기능 추가)
st.header("💬 Interactive Learning")
input_method = st.radio("Choose input method:", ("Text", "Voice"))

if input_method == "Text":
    user_input = st.text_input("Ask a question about the story, characters, or language:")
else:
    if st.button("🎤 Start Voice Input"):
        user_input = recognize_speech()
        st.write(f"You said: {user_input}")
        
        # 음성 인식 정확도 평가 및 표시
        current_line = initial_script[st.session_state.current_line]
        accuracy = evaluate_speech_accuracy(current_line, user_input)
        st.write(f"Speech recognition accuracy: {accuracy:.2f}%")
        
        if accuracy >= 90:
            st.success("Excellent pronunciation!")
        elif accuracy >= 70:
            st.info("Good pronunciation. Keep practicing!")
        else:
            st.warning("Your pronunciation needs some work. Try again!")

if st.button("🚀 Submit"):
    with st.spinner("AI Tutor is thinking..."):
        ai_response = generate_response(user_input)
    st.success("AI Tutor: " + ai_response)
    if st.button("🔊 Listen to AI response"):
        text_to_speech(ai_response)

# 대화 기록 표시 (기존 코드와 동일)
st.header("📜 Conversation History")
for message in st.session_state.conversation_history:
    if message['role'] == 'user':
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**AI Tutor:** {message['content']}")
