import streamlit as st
import google.generativeai as genai
import os

# --- การตั้งค่าหน้าเว็บหลัก ---
st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

# --- การตกแต่ง UI ด้วย CSS เพื่อให้เหมือนรูปภาพตัวอย่าง ---
st.markdown("""
<style>
    /* ตั้งค่าสีพื้นหลังหลักของแอปเป็นสีขาว */
    .stApp { background-color: #FFFFFF !important; color: black !important; }

    /* ตกแต่งแถบด้านข้าง (Sidebar) ด้วยสีเขียวอ่อน */
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }

    /* ตั้งค่าสีข้อความทั่วไปและหัวข้อเป็นสีเขียวเข้ม */
    h1, h2, h3, p, span, div { color: #00594C; }

    /* ตกแต่งกล่องข้อความแชท */
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }

    /* ปรับสีข้อความภายในแชท */
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# --- ส่วนของการเชื่อมต่อ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

# --- โหลดโมเดล Gemini ---
@st.cache_resource
def load_model():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search": {}}])
        return model
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดโมเดล: {e}")
    return None

model = load_model()

if not model:
    st.error("❌ ไม่พบโมเดลที่ใช้งานได้")
    st.stop()

# --- หัวข้อหน้าเว็บ ---
st.title("AI TEST")

# --- โหลดฐานข้อมูล (ถ้ามี) ---
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูลมหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตศรีราชา"

# --- ส่วนแสดงข้อความแชท (Chat History) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- ส่วนรับข้อความใหม่ (Input field) ---
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    # แสดงข้อความของผู้ใช้
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ประมวลผลและแสดงคำตอบจาก Assistant
    with st.chat_message("assistant", avatar="🦖"):
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ หากถามเรื่องตึก ต้องส่งลิ้งค์แผนที่เสมอ "
            "หากนิสิตถามเรื่องรถติดหรือสภาพจราจร ให้ใช้ Google Search เพื่อสรุปคำตอบให้เขาด้วย"
        )
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            # ใช้ st.spinner เพื่อแสดงสถานะการโหลด
            with st.spinner("พี่กำลังหาข้อมูลอยู่ครับ..."):
                response = model.generate_content(full_prompt)
            
            # แสดงคำตอบ
            if response and response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.write("พี่กำลังหาข้อมูลอยู่ครับ ลองถามอีกทีนะ")
        except Exception as e:
            st.error(f"❌ ระบบขัดข้อง: {e}")
