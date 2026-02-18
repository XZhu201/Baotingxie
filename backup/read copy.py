import os
import base64
from openai import OpenAI
import pyttsx3

str_figname = "wansita.jpg"

# ========= 1) 读取环境变量 =========
API_KEY = os.getenv("ARK_API_KEY")
ENDPOINT_ID = os.getenv("ARK_ENDPOINT_ID")  # 形如 ep-xxxxxx

if not API_KEY:
    raise ValueError("未找到环境变量 ARK_API_KEY")

if not ENDPOINT_ID:
    raise ValueError("未找到环境变量 ARK_ENDPOINT_ID（请填你控制台创建的 ep-xxxx 接入点 ID）")

# ========= 2) 初始化 Ark 客户端 =========
client = OpenAI(
    api_key=API_KEY,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# ========= 3) 读取图片并转 base64 =========
image_path = str_figname  # 改成你的图片文件名

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

base64_image = encode_image(image_path)

# ========= 4) 调用模型做 OCR =========
response = client.chat.completions.create(
    model=ENDPOINT_ID,  # 注意：这里必须是 ep-xxxx
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请直接提取图片中的所有可见文字，不要添加任何解释。只输出纯文字，按阅读顺序输出。"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ],
        }
    ],
    max_tokens=800,
    temperature=0.2,
)

extracted_text = (response.choices[0].message.content or "").strip()

print("豆包提取到的文字：")
print(extracted_text)

# ========= 5) 本地朗读（pyttsx3） =========
if extracted_text:
    engine = pyttsx3.init()
    engine.setProperty("rate", 90)
    engine.setProperty("volume", 1.0)

    # 尝试优先选中文声音（不保证每台机器都有）
    voices = engine.getProperty("voices")
    for voice in voices:
        if "chinese" in voice.name.lower() or "xiaoxiao" in voice.id.lower():
            engine.setProperty("voice", voice.id)
            break

    engine.say(extracted_text)
    engine.runAndWait()
    print("朗读完成！")
else:
    print("没有提取到文字。")