import openai
import streamlit as st
from gtts import gTTS
from io import BytesIO

# OpenAI 클라이언트 설정
client = openai.OpenAI(api_key=st.secrets['API_KEY'])

# 초기 스크립트 (변경 없음)
initial_script = [
    "It's a beautiful fall morning on the farm. The leaves are turning yellow and red. Fern comes to visit Wilbur, her favorite pig.",
    "Fern: Good morning, Wilbur! How are you today?",
    "Wilbur: Oh, Fern! I'm so happy to see you. I was feeling a little lonely.",
    "Fern: Don't be lonely, Wilbur. You have so many friends here on the farm!",
    "Charlotte: (coming down from her web) Good morning, Fern. You're right, Wilbur has many friends, including me.",
    "Wilbur: Charlotte! I'm so glad you're here. Fern, isn't Charlotte amazing? She can make the most beautiful webs.",
    "Fern: Yes, Charlotte's webs are beautiful. But Wilbur, I heard some bad news. The farmers are talking about... (whispers) making you into bacon.",
    "Wilbur: (frightened) Oh no! What can I do? I don't want to be bacon!",
    "Charlotte: Don't worry, Wilbur. I have an idea to save you.",
    "Fern: Really, Charlotte? What's your idea?",
    "Charlotte: I'm going to write a message about Wilbur in my web. Something that will make the humans see how special he is.",
    "Wilbur: You can write? That's amazing, Charlotte!",
    "Charlotte: Yes, I can. Now, I need to think of the perfect words. It will take me all night to write them.",
    "That night, after everyone has gone to sleep, Charlotte begins her work. She moves back and forth, up and down, spinning her web and writing her message.",
    "Wilbur: (waking up) Charlotte? What are you doing up so late?",
    "Charlotte: I'm writing the message, Wilbur. Go back to sleep. You'll see it in the morning.",
    "In the morning, Farmer Zuckerman comes to feed the animals. He walks towards the barn, not knowing about the surprise waiting for him.",
    "Farmer Zuckerman: (enters and stops suddenly) What in the world? The spider web... it has words in it!",
    "Farmer Zuckerman: (reading aloud) SOME PIG! Well I've never seen anything like this in all my years of farming!",
    "Wilbur: (excited) Charlotte, they noticed! They really noticed!",
    "Charlotte: (softly) This is just the beginning, Wilbur. Keep watching.",
    "Word spreads quickly about the amazing spider web. Many people come to see it, and the farm becomes very busy.",
    "Fern: (running in) Uncle Zuckerman! Is it true? Did Charlotte really write about Wilbur?",
    "Farmer Zuckerman: It's true, Fern! Come and see for yourself. It's the most amazing thing!",
    "Fern: (looking at the web) Oh, Wilbur! You really are some pig!",
    "Wilbur: (to Charlotte) Do you think this will save me, Charlotte?",
    "Charlotte: I hope so, Wilbur. We'll keep trying. I'll write more messages if we need to.",
    "Farmer Zuckerman: (proudly) This pig is special. We can't turn him into bacon now. He's famous!",
    "Fern: (hugging Wilbur) Did you hear that, Wilbur? You're safe now!",
    "Wilbur: (happily) Oh, thank you, Charlotte! You saved my life!",
]

# 세션 상태 변수 초기화 (변경 없음)
if 'current_line' not in st.session_state:
    st.session_state.current_line = 0
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# 사용자 정의 CSS (변경 없음)
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

st.title("🕷️ 지천초 2024 3학년 대본 🐷")

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes.read(), format='audio/mp3')

def generate_response(prompt):
    st.session_state.conversation_history.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI tutor helping a student learn English through the story of Charlotte's Web. Provide explanations, answer questions, and engage in dialogue about the story, characters, and language used. Keep your responses appropriate for young learners."},
                *st.session_state.conversation_history
            ]
        )

        ai_response = response.choices[0].message.content.strip()
        st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I'm sorry, an error occurred. Please try again."

# 사이드바와 전체 스크립트 (변경 없음)
st.sidebar.header("Full Script")
for i, line in enumerate(initial_script):
    st.sidebar.markdown(f'<div class="script-line">{line}</div>', unsafe_allow_html=True)
    if st.sidebar.button(f"🔊 Listen", key=f"listen_{i}"):
        text_to_speech(line)

# 순차적 듣기 섹션 (변경 없음)
st.header("🎧 Sequential Listening")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⏮️ Previous Line") and st.session_state.current_line > 0:
        st.session_state.current_line -= 1

with col2:
    if st.button("▶️ Listen to Current Line"):
        text_to_speech(initial_script[st.session_state.current_line])

with col3:
    if st.button("⏭️ Next Line") and st.session_state.current_line < len(initial_script) - 1:
        st.session_state.current_line += 1

st.info(f"Current Line: {initial_script[st.session_state.current_line]}")

# 대화형 학습 섹션 (변경 없음)
st.header("💬 Interactive Learning")
user_input = st.text_input("Ask a question about the story, characters, or language:")

if st.button("🚀 Submit") and user_input:
    with st.spinner("AI Tutor is thinking..."):
        ai_response = generate_response(user_input)
    st.success("AI Tutor: " + ai_response)
    if st.button("🔊 Listen to AI Response"):
        text_to_speech(ai_response)

# 대화 기록 (변경 없음)
st.header("📜 Conversation History")
for message in st.session_state.conversation_history:
    if message['role'] == 'user':
        st.markdown(f"**User:** {message['content']}")
    else:
        st.markdown(f"**AI Tutor:** {message['content']}")
