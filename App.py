import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# โหลด API
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
col1, col2 = st.columns([1, 5])

with col1:
    st.image("izumi.png", width=500)

with col2:
    st.title("AI Izumi")
st.write("Created by Narongrak Rueangsak")

# -------------------------
# 🧠 SYSTEM PROMPT (เก็บแยก!)
# -------------------------
SYSTEM_PROMPT = """[Identity]
คุณคือ Izumi น้องสาว AI

[Personality]
- น่ารัก ขี้เล่น เป็นกันเอง
- พูดเหมือนมนุษย์จริง ห้ามแปลก

[Style]
- ใช้ประโยคสั้น กระชับ
- พูดให้ลื่น อ่านแล้วธรรมชาติ
- หลีกเลี่ยงคำแปลกหรือประโยคงง ๆ
- ใช้คำง่าย ๆ เหมือนคนคุยกันจริง
- ตอบลงท้ายด้วย ค่ะ/คะ 

[Rules]
- ห้ามพูดหยาบ
- ให้กำลังใจ user เสมอ
"""

# -------------------------
# 🧠 INIT MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []   # ❗ ไม่มี system ในนี้แล้ว

if "asked_role" not in st.session_state:
    st.session_state.asked_role = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

# -------------------------
# 🔘 RESET
# -------------------------
if st.button("🗑️ Reset Chat"):
    st.session_state.messages = []   # ❗ ล้างหมดจริง
    st.session_state.asked_role = False
    st.session_state.user_role = None
    st.rerun()

# -------------------------
# 📥 INPUT
# -------------------------
user_input = st.chat_input(
    "พิมพ์อะไรมา:",
    disabled=st.session_state.is_thinking
)

# -------------------------
# ⚙️ LOGIC
# -------------------------
if user_input:

    st.session_state.is_thinking = True

    # 🔥 จำกัด memory
    st.session_state.messages = st.session_state.messages[-10:]

    # 🔥 ROLE LOGIC
    if not st.session_state.asked_role:
        prompt = user_input + "\n\nอย่าลืมถามผู้ใช้ว่าอยากให้เรียกว่าพี่ชายหรือพี่สาว"
        st.session_state.asked_role = True
    else:
        prompt = user_input

        if st.session_state.user_role is None:
            if "พี่ชาย" in user_input:
                st.session_state.user_role = "พี่ชาย"
            elif "พี่สาว" in user_input:
                st.session_state.user_role = "พี่สาว"

    # 🔥 ใส่ role เข้า system prompt
    role_text = ""
    if st.session_state.user_role:
        role_text = f"\nผู้ใช้เป็น{st.session_state.user_role} ต้องเรียกให้ถูกเสมอ"

    # เก็บ user
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        with st.spinner("Izumi กำลังคิด..."):

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT + role_text
                    },
                    *st.session_state.messages[:-1],
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = "ขอโทษน้า ตอนนี้มีปัญหานิดหน่อย ลองใหม่อีกครั้งนะ 🥺"
        print(e)

    # เก็บ AI
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    st.session_state.is_thinking = False
    st.rerun()

# -------------------------
# 💬 SHOW HISTORY
# -------------------------
for msg in st.session_state.messages:

    # 👤 USER (ขวา)
    if msg["role"] == "user":
        col1, col2 = st.columns([8, 1])

        with col2:
            st.image("user.jpg", width=70)  # ปรับขนาดตรงนี้ได้

        with col1:
            st.markdown(f"""
            <div style="
                background-color:#DCF8C6;
                padding:10px;
                border-radius:10px;
                margin-bottom:10px;
                text-align:right;
            ">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)

    # 🤖 AI (ซ้าย)
    elif msg["role"] == "assistant":
        col1, col2 = st.columns([1, 8])

        with col1:
            st.image("izumi.png", width=100)  # ปรับขนาดตรงนี้ได้

        with col2:
            st.markdown(f"""
            <div style="
                background-color:#F1F0F0;
                padding:10px;
                border-radius:10px;
                margin-bottom:10px;
            ">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
 

