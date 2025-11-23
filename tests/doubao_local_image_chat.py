import os
import base64
from pathlib import Path

from openai import OpenAI  # pip install openai


# ===== 这里两项你要自己填 =====
# 建议把 API Key 放到环境变量 ARK_API_KEY 里，这里就不用写死
API_KEY = os.getenv("ARK_API_KEY") or "968442b0-1939-40fa-bf38-3a1ed9410a02"

# 视觉模型或推理接入点 ID，例如：
#   doubao-seed-1-6-vision-250815
#   doubao-1-5-vision-pro-32k-250115
MODEL_ID = "doubao-seed-1-6-vision-250815"
# ===============================


def encode_image(img_path: Path) -> str:
    """读取本地图片并转成 base64 字符串"""
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    img_path = Path("F:\\Projects\\suno\\imag.png")  # 默认测项目根目录下的 imag.png
    if not img_path.exists():
        print(f"❌ 找不到图片: {img_path}")
        return

    if not API_KEY:
        print("❌ 未设置 ARK_API_KEY，请先配置环境变量或在脚本中填入 API_KEY")
        return

    # 初始化豆包/方舟兼容客户端



    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=API_KEY,
    )

    # 本地图片 → base64
    b64 = encode_image(img_path)

    # 根据图片格式设置 MIME，这里假设是 PNG；如果是 JPG 就改成 image/jpeg
    image_url = f"data:image/png;base64,{b64}"

    print("⏳ 发送本地图片到豆包视觉模型...")
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "描述图片主体、场景和情绪，并给一句中文标题。"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
    )

    print("\n=== 返回内容 ===")
    choice = resp.choices[0].message.content
    print(choice)


if __name__ == "__main__":
    main()
