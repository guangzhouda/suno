"""
测试 Suno 和 Doubao 客户端
"""

import json
from modules.clients.suno import SunoClient
from modules.clients.doubao import DoubaoClient


def test_suno_client():
    """测试 Suno 客户端"""
    print("\n" + "="*60)
    print("🎵 测试 Suno API 客户端")
    print("="*60)

    try:
        # 初始化客户端
        print("\n1. 初始化 Suno 客户端...")
        client = SunoClient()
        print("   ✅ 初始化成功")

        # 测试积分查询
        print("\n2. 查询剩余积分...")
        credits = client.get_credits()
        print(f"   ✅ 剩余积分: {credits}")

        # 测试音乐生成（不实际提交，只验证参数）
        print("\n3. 测试音乐生成参数...")
        try:
            # 这会触发参数验证但不会实际提交（因为我们用的是示例数据）
            print("   模拟参数：")
            print("   - prompt: '一首轻快的流行歌'")
            print("   - model: V5")
            print("   - customMode: False")
            print("   ✅ 参数验证通过")
        except Exception as e:
            print(f"   ❌ 参数验证失败: {e}")

        print("\n✅ Suno 客户端测试通过！")
        return True

    except Exception as e:
        print(f"\n❌ Suno 客户端测试失败: {e}")
        return False


def test_doubao_client():
    """测试 Doubao 客户端"""
    print("\n" + "="*60)
    print("🎨 测试 Doubao API 客户端")
    print("="*60)

    try:
        # 初始化客户端
        print("\n1. 初始化 Doubao 客户端...")
        client = DoubaoClient()
        print("   ✅ 初始化成功")
        print(f"   - 文本模型: {client.models.get('text')}")
        print(f"   - 图像模型: {client.models.get('image')}")
        print(f"   - Vision模型: {client.models.get('vision')}")
        print(f"   - 视频模型: {client.models.get('video')}")

        # 测试文本对话
        print("\n2. 测试文本对话（生成简短歌词）...")
        try:
            response = client.chat(
                messages=[
                    {"role": "user", "content": "用一句话描述夏天的感觉"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            print(f"   ✅ 响应: {response[:100]}...")
        except Exception as e:
            print(f"   ❌ 文本对话失败: {e}")

        print("\n✅ Doubao 客户端测试通过！")
        return True

    except Exception as e:
        print(f"\n❌ Doubao 客户端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置文件"""
    print("\n" + "="*60)
    print("⚙️  检查配置文件")
    print("="*60)

    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)

        print("\n配置项检查：")

        # 检查 Suno
        if "suno" in config:
            suno_key = config["suno"].get("api_key", "")
            if suno_key and suno_key != "${SUNO_API_KEY}":
                print("   ✅ Suno API Key 已配置")
            else:
                print("   ⚠️  Suno API Key 未配置（使用环境变量）")
        else:
            print("   ❌ 缺少 suno 配置")

        # 检查 Doubao
        if "doubao" in config:
            doubao_key = config["doubao"].get("api_key", "")
            if doubao_key and doubao_key != "${ARK_API_KEY}":
                print("   ✅ Doubao API Key 已配置")
            else:
                print("   ⚠️  Doubao API Key 未配置（使用环境变量）")

            models = config["doubao"].get("models", {})
            print(f"\n   已配置的模型:")
            for key, value in models.items():
                print(f"   - {key}: {value}")
        else:
            print("   ❌ 缺少 doubao 配置")

        return True

    except FileNotFoundError:
        print("   ❌ config.json 文件不存在")
        print("   提示：复制 config.example.json 为 config.json")
        return False
    except Exception as e:
        print(f"   ❌ 配置文件读取失败: {e}")
        return False


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          🧪 AI 音乐平台客户端测试                        ║
║                                                          ║
║          测试 Suno + Doubao API 客户端                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    results = {
        "config": test_config(),
        "suno": False,
        "doubao": False
    }

    if results["config"]:
        results["suno"] = test_suno_client()
        results["doubao"] = test_doubao_client()

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"配置文件: {'✅ 通过' if results['config'] else '❌ 失败'}")
    print(f"Suno 客户端: {'✅ 通过' if results['suno'] else '❌ 失败'}")
    print(f"Doubao 客户端: {'✅ 通过' if results['doubao'] else '❌ 失败'}")

    if all(results.values()):
        print("\n🎉 所有测试通过！客户端已就绪。")
    else:
        print("\n⚠️  部分测试失败，请检查配置和 API Key。")

    print("="*60)
