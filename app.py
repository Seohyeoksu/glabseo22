import os
import openai
import streamlit as st
import base64
from difflib import SequenceMatcher

# For audio recording and playback
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import numpy as np
import threading
import queue

# OpenAI API key setup
openai.api_key = st.secrets['API_KEY']

# Initial script
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

st.title("🕷️ Charlotte's Web Interactive Learning 🐷")

def text_to_speech(text):
    # Use a TTS API or library that supports in-memory audio
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
            model="gpt-4o",
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

def recognize_speech():
    # Function to process audio frames
    pass  # This will be handled by streamlit_webrtc

def evaluate_speech_accuracy(original_text, recognized_text):
    similarity = SequenceMatcher(None, original_text.lower(), recognized_text.lower()).ratio()
    return similarity * 100

st.sidebar.header("Full Script")
for i, line in enumerate(initial_script):
    st.sidebar.markdown(f'<div class="script-line">{line}</div>', unsafe_allow_html=True)
    if st.sidebar.button(f"🔊 Listen", key=f"listen_{i}"):
        text_to_speech(line)

# Sequential Listening
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

st.info(f"Current line: {initial_script[st.session_state.current_line]}")

# Interactive Learning Section
st.header("💬 Interactive Learning")
input_method = st.radio("Choose input method:", ("Text", "Voice"))

if input_method == "Text":
    user_input = st.text_input("Ask a question about the story, characters, or language:")
else:
    st.write("녹음을 시작하려면 'Start'를 클릭하세요.")
    # WebRTC 설정
    RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

    from streamlit_webrtc import AudioProcessorBase

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.audio_frames = []

        def recv(self, frame):
            # 오디오 프레임 수집
            self.audio_frames.append(frame)
            return frame

    webrtc_ctx = webrtc_streamer(
        key="speech-recognition",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=AudioProcessor,
        async_processing=True,
    )

    if webrtc_ctx.audio_processor:
        if st.button("Process Audio"):
            st.write("오디오를 처리 중입니다...")
            # 모든 오디오 프레임 결합
            audio_frames = webrtc_ctx.audio_processor.audio_frames

            # 오디오 프레임을 하나의 오디오 세그먼트로 변환
            from pydub import AudioSegment
            from io import BytesIO

            combined = AudioSegment.empty()
            for frame in audio_frames:
                audio = frame.to_ndarray()
                sound = AudioSegment(
                    data=audio.tobytes(),
                    sample_width=audio.dtype.itemsize,
                    frame_rate=frame.sample_rate,
                    channels=len(frame.layout.channels),
                )
                combined += sound

            # 결합된 오디오를 BytesIO 버퍼에 저장
            audio_buffer = BytesIO()
            combined.export(audio_buffer, format="wav")
            audio_buffer.seek(0)

            # SpeechRecognition을 사용하여 음성 인식
            import speech_recognition as sr

            r = sr.Recognizer()
            with sr.AudioFile(audio_buffer) as source:
                audio_data = r.record(source)
                try:
                    user_input = r.recognize_google(audio_data)
                    st.write(f"You said: {user_input}")

                    # 음성 인식 정확도 평가
                    current_line = initial_script[st.session_state.current_line]
                    accuracy = evaluate_speech_accuracy(current_line, user_input)
                    st.write(f"Speech recognition accuracy: {accuracy:.2f}%")

                    if accuracy >= 90:
                        st.success("Excellent pronunciation!")
                    elif accuracy >= 70:
                        st.info("Good pronunciation. Keep practicing!")
                    else:
                        st.warning("Your pronunciation needs some work. Try again!")
                except sr.UnknownValueError:
                    st.error("음성을 이해할 수 없습니다.")
                except sr.RequestError:
                    st.error("음성 인식 서비스에 요청할 수 없습니다.")
        else:
            st.write("녹음을 마친 후 'Process Audio'를 눌러주세요.")

if st.button("🚀 Submit") and 'user_input' in locals():
    with st.spinner("AI Tutor is thinking..."):
        ai_response = generate_response(user_input)
    st.success("AI Tutor: " + ai_response)
    if st.button("🔊 Listen to AI response"):
        text_to_speech(ai_response)

st.header("📜 Conversation History")
for message in st.session_state.conversation_history:
    if message['role'] == 'user':
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**AI Tutor:** {message['content']}")
