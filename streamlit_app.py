import os
import base64
import io
import re
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import streamlit as st
from gtts import gTTS

# ========= 1) 加载 .env =========
load_dotenv()  # 会加载同目录下的 .env 文件

API_KEY = os.getenv("ARK_API_KEY")
ENDPOINT_ID = os.getenv("ARK_ENDPOINT_ID")

if not API_KEY or not ENDPOINT_ID:
    st.error("请在 .env 文件中设置 ARK_API_KEY 和 ARK_ENDPOINT_ID")
    st.stop()

# ========= 2) 初始化 Ark 客户端 =========
client = OpenAI(
    api_key=API_KEY,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# ========= 3) Streamlit 页面 =========
st.title("图片文字提取 & 网页朗读（火山方舟 OCR）")

uploaded_file = st.file_uploader("上传图片（jpg/png）", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="上传图片", use_column_width=True)

    # 转 base64
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    base64_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    # ========= 4) 调用火山方舟 OCR =========
    with st.spinner("正在提取文字..."):
        response = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请直接提取图片中的所有可见文字，不要添加任何解释，只输出纯文字。按阅读顺序输出。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ],
            max_tokens=800,
            temperature=0.2,
        )

    extracted_text = (response.choices[0].message.content or "").strip()

    st.subheader("提取文字")
    st.text(extracted_text)

    # ========= 5) 生成语音 =========
    if extracted_text:
        tts = gTTS(text=extracted_text, lang='zh')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3")