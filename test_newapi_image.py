"""
直接测试 New API 图片生成功能
"""

import requests
import json
import time

# 配置
API_KEY = "sk-8iPAxpcfZrJs836lMuZuTv65D5Pu49r8zTFICWEbz4Ii0MNe"
API_BASE = "https://api.voct.top/v1"
MODEL = "doubao-seedream-4-0-250828"

def test_image_generation():
    """测试图片生成"""
    print("=" * 60)
    print("开始测试 New API 图片生成功能")
    print("=" * 60)

    url = f"{API_BASE}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "prompt": "一只可爱的小猫坐在窗台上，温暖的阳光",
        "n": 1,
        "size": "1024x1024",
        "response_format": "url"
    }

    print(f"\n📍 请求地址: {url}")
    print(f"📦 请求模型: {MODEL}")
    print(f"✏️  提示词: {payload['prompt']}")
    print(f"📐 图片尺寸: {payload['size']}")
    print("\n⏳ 开始请求（可能需要 30-120 秒）...\n")

    start_time = time.time()

    try:
        # 发送请求，设置180秒超时
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=180
        )

        elapsed_time = time.time() - start_time
        print(f"⏱️  请求耗时: {elapsed_time:.2f} 秒")
        print(f"📊 HTTP状态码: {response.status_code}")

        # 检查状态码
        if response.status_code == 200:
            print("✅ 请求成功！\n")

            # 解析响应
            result = response.json()
            print("📦 完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 提取图片URL
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0].get('url')
                if image_url:
                    print(f"\n🖼️  图片URL: {image_url}")
                    print("\n✅ 图片生成成功！你可以在浏览器打开上面的URL查看图片")
                else:
                    print("\n⚠️  响应中没有找到图片URL")
            else:
                print("\n⚠️  响应格式不符合预期")

        else:
            print(f"❌ 请求失败！HTTP {response.status_code}")
            print(f"\n错误响应内容:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)

    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"❌ 请求超时！({elapsed_time:.2f} 秒)")
        print("图片生成可能需要更长时间，建议稍后重试")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        print("请检查网络连接")

    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)


def test_text_generation():
    """测试文本生成（快速测试API是否可用）"""
    print("\n" + "=" * 60)
    print("快速测试：文本生成（验证API Key是否有效）")
    print("=" * 60)

    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 20
    }

    print(f"\n📍 请求地址: {url}")
    print("⏳ 测试中...\n")

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            print("✅ 文本API正常！API Key 有效")
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"💬 AI回复: {content}")
            return True
        else:
            print(f"❌ 文本API失败！HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ 文本API测试失败: {e}")
        return False


if __name__ == "__main__":
    # 先测试文本API（快速验证）
    text_ok = test_text_generation()

    if text_ok:
        print("\n\n")
        # 再测试图片生成
        test_image_generation()
    else:
        print("\n⚠️  文本API测试失败，跳过图片生成测试")
        print("请检查：")
        print("  1. API Key 是否正确")
        print("  2. 网络连接是否正常")
        print("  3. API 服务是否可用")
