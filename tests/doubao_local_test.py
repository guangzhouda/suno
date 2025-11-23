import requests
import pathlib

API_KEY = "968442b0-1939-40fa-bf38-3a1ed9410a02"   # 必填，记得换成你自己的

def test_local_image():
    img_path = pathlib.Path("F:\\Projects\\suno\\imag.png")
    if not img_path.exists():
        print("❌ 找不到 imag.png")
        return

    url = "https://ark.cn-beijing.volces.com/api/v3/vision/understand"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    files = {
        "image": open(img_path, "rb")
    }

    data = {
        "question": "描述这张图片的内容。"
    }

    print("⏳ 正在向豆包发送本地图片...")
    r = requests.post(url, headers=headers, files=files, data=data, timeout=60)

    print("\n=== 豆包返回 ===")
    print("状态码：", r.status_code)
    print("响应：", r.text)

if __name__ == "__main__":
    test_local_image()
