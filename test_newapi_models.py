"""
测试New API的两个模型
1. 文本模型：DeepSeek-V3
2. 图像模型：doubao-seedream-4-0-250828
"""

import os
import requests
import json
from datetime import datetime

# ==================== 配置读取 ====================

def get_config():
    """从环境变量或配置文件读取配置"""
    config = {
        'api_base': os.getenv('NEWAPI_API_BASE', 'https://api.voct.top'),
        'api_key': os.getenv('NEWAPI_API_KEY', ''),
        'text_model': os.getenv('TEXT_MODEL', 'deepseek-ai/DeepSeek-V3'),
        'image_model': os.getenv('IMAGE_MODEL', 'doubao-seedream-4-0-250828')
    }

    # 尝试从config.json读取
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                file_config = json.load(f)

                # 从newapi配置读取
                if 'newapi' in file_config:
                    newapi_config = file_config['newapi']
                    config['api_base'] = newapi_config.get('api_base', config['api_base'])
                    config['api_key'] = newapi_config.get('api_key', config['api_key'])
                    config['text_model'] = newapi_config.get('text_model', config['text_model'])
                    config['image_model'] = newapi_config.get('image_model', config['image_model'])
        except Exception as e:
            print(f"⚠️ 读取config.json失败: {e}")

    return config


# ==================== API测试函数 ====================

def test_text_model(config):
    """测试文本模型"""
    print("\n" + "="*60)
    print("📝 测试文本模型（DeepSeek-V3）")
    print("="*60)

    api_base = config['api_base'].rstrip('/')
    api_key = config['api_key']
    model = config['text_model']

    if not api_key:
        print("❌ 错误：未配置NEWAPI_API_KEY")
        return False

    print(f"API地址: {api_base}")
    print(f"模型: {model}")
    print(f"API密钥: {api_key[:10]}..." if len(api_key) > 10 else "***")

    url = f"{api_base}/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "你好，请用一句话介绍你自己。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    try:
        print(f"\n🔄 发送请求...")
        print(f"POST {url}")

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # 打印响应结构
            print(f"\n✅ 请求成功！")
            print(f"\n响应数据：")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 提取并显示回复内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"\n💬 模型回复：")
                print(f"{content}")

                # 显示token使用情况
                if 'usage' in result:
                    usage = result['usage']
                    print(f"\n📊 Token使用：")
                    print(f"  输入: {usage.get('prompt_tokens', 0)}")
                    print(f"  输出: {usage.get('completion_tokens', 0)}")
                    print(f"  总计: {usage.get('total_tokens', 0)}")

            return True
        else:
            print(f"\n❌ 请求失败")
            print(f"错误信息: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（30秒）")
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def test_image_model(config):
    """测试图像生成模型"""
    print("\n" + "="*60)
    print("🖼️ 测试图像生成模型（doubao-seedream）")
    print("="*60)

    api_base = config['api_base'].rstrip('/')
    api_key = config['api_key']
    model = config['image_model']

    if not api_key:
        print("❌ 错误：未配置NEWAPI_API_KEY")
        return False

    print(f"API地址: {api_base}")
    print(f"模型: {model}")
    print(f"API密钥: {api_key[:10]}..." if len(api_key) > 10 else "***")

    url = f"{api_base}/v1/images/generations"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
        "model": model,
        "prompt": "一只可爱的小猫坐在窗台上，温暖的阳光照进来，温馨治愈的画风",
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "response_format": "url"
    }

    try:
        print(f"\n🔄 发送请求...")
        print(f"POST {url}")
        print(f"提示词: {payload['prompt']}")

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ 请求成功！")
            print(f"\n响应数据：")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 提取图片URL
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0].get('url', '')
                print(f"\n🖼️ 生成的图片URL：")
                print(f"{image_url}")

                if image_url:
                    print(f"\n💡 提示：在浏览器中打开上面的URL可以查看生成的图片")

            return True
        else:
            print(f"\n❌ 请求失败")
            print(f"错误信息: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（60秒）")
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


# ==================== 主程序 ====================

def main():
    print("="*60)
    print("🧪 New API 模型测试工具")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 读取配置
    config = get_config()

    print(f"\n📋 当前配置：")
    print(f"  API地址: {config['api_base']}")
    print(f"  API密钥: {'已配置' if config['api_key'] else '未配置'}")
    print(f"  文本模型: {config['text_model']}")
    print(f"  图像模型: {config['image_model']}")

    if not config['api_key']:
        print("\n" + "="*60)
        print("❌ 错误：未找到API密钥配置")
        print("="*60)
        print("\n请设置环境变量或在config.json中配置：")
        print("\n方式1：环境变量")
        print("  export NEWAPI_API_KEY='your-key'")
        print("  export NEWAPI_API_BASE='https://api.voct.top'")
        print("\n方式2：config.json")
        print('  {')
        print('    "newapi": {')
        print('      "api_key": "your-key",')
        print('      "api_base": "https://api.voct.top",')
        print('      "text_model": "deepseek-ai/DeepSeek-V3",')
        print('      "image_model": "doubao-seedream-4-0-250828"')
        print('    }')
        print('  }')
        return

    # 测试文本模型
    text_ok = test_text_model(config)

    # 测试图像模型
    image_ok = test_image_model(config)

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"文本模型 ({config['text_model']}): {'✅ 通过' if text_ok else '❌ 失败'}")
    print(f"图像模型 ({config['image_model']}): {'✅ 通过' if image_ok else '❌ 失败'}")
    print("="*60)

    if text_ok and image_ok:
        print("\n🎉 所有测试通过！可以正常使用这两个模型。")
    elif text_ok or image_ok:
        print("\n⚠️ 部分测试通过，请检查失败的模型配置。")
    else:
        print("\n❌ 所有测试失败，请检查API配置和网络连接。")


if __name__ == "__main__":
    main()
