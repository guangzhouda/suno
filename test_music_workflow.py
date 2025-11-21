"""
测试 AI 音乐创作工作流

演示如何使用不同的模板创作音乐
"""

import requests
import json
from typing import Dict, Any

# API 基础地址
API_BASE = "http://localhost:8000"


def test_workflow(
    template: str,
    user_input: str,
    auto_generate_music: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    测试工作流

    Args:
        template: 模板ID
        user_input: 用户输入
        auto_generate_music: 是否自动生成音乐
        **kwargs: 其他参数
    """
    url = f"{API_BASE}/api/music-workflow/create"

    payload = {
        "template": template,
        "user_input": user_input,
        "auto_generate_music": auto_generate_music,
        "wait_for_completion": False,
        **kwargs
    }

    print(f"\n{'='*60}")
    print(f"🎵 测试模板: {template}")
    print(f"📝 用户输入: {user_input[:50]}...")
    print(f"{'='*60}\n")

    try:
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()

            if result.get('success'):
                print("✅ 工作流执行成功！\n")

                lyrics_data = result.get('lyrics_data', {})
                print(f"📌 歌曲标题: {lyrics_data.get('title', '未命名')}")
                print(f"🎨 风格: {lyrics_data.get('style', 'N/A')}")
                print(f"💭 情绪: {lyrics_data.get('emotion', 'N/A')}")

                if lyrics_data.get('reasoning'):
                    print(f"\n💡 创作思路:")
                    print(f"   {lyrics_data['reasoning']}")

                lyrics_text = result.get('lyrics_text')
                if lyrics_text:
                    print(f"\n📄 完整歌词:")
                    print("-" * 40)
                    print(lyrics_text)
                    print("-" * 40)

                if result.get('music_task_id'):
                    print(f"\n🎶 Suno Task ID: {result['music_task_id']}")
                else:
                    print("\n⚠️  未启用音乐生成")

                return result
            else:
                print(f"❌ 工作流失败: {result.get('error')}")
                print(f"   失败步骤: {result.get('step_failed')}")
                return result
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(response.text)
            return {}

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return {}


def get_templates() -> Dict[str, Any]:
    """获取所有可用模板"""
    url = f"{API_BASE}/api/music-workflow/templates"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {})
        else:
            print(f"获取模板失败: {response.status_code}")
            return {}
    except Exception as e:
        print(f"获取模板失败: {e}")
        return {}


def show_templates():
    """显示所有可用的模板"""
    print("\n" + "="*60)
    print("📚 可用的创作模板")
    print("="*60 + "\n")

    templates_data = get_templates()
    templates = templates_data.get('templates', [])

    if not templates:
        print("⚠️  无法获取模板列表")
        return

    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['icon']} {template['name']} (ID: {template['id']})")
        print(f"   {template['description']}")
        print()


# ==================== 测试案例 ====================

def test_case_1_inspiration():
    """测试案例1：灵感写歌"""
    test_workflow(
        template="inspiration_songwriting",
        user_input="想写一首关于跨年夜独自在城市街头的歌，有点孤独但也有期待新年的感觉，适合一个人安静听的那种",
        auto_generate_music=False
    )


def test_case_2_rewrite():
    """测试案例2：歌词改写"""
    original_lyrics = """
[主歌1]
夜色渐深 街灯昏黄
孤单的身影 拉得很长
人群熙攘 我却迷惘
不知该往何方

[副歌]
这城市太大 我太渺小
找不到温暖的怀抱
倒计时响起 新年要到
心中的愿望 有谁知道
"""

    test_workflow(
        template="lyrics_rewrite",
        user_input="将这首歌从孤独改写为温暖治愈的感觉",
        original_lyrics=original_lyrics,
        mode="change_theme",
        target_theme="温暖治愈",
        auto_generate_music=False
    )


def test_case_3_quick():
    """测试案例3：快速生成"""
    test_workflow(
        template="quick_generation",
        user_input="夏天、海边、夕阳、吉他、青春",
        auto_generate_music=False
    )


def test_case_4_healing():
    """测试案例4：情绪疗愈"""
    test_workflow(
        template="emotional_healing",
        user_input="最近工作压力很大，失眠，想要一首能让我放松下来的歌",
        auto_generate_music=False
    )


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          🎵 AI 音乐创作工作流测试                        ║
║                                                          ║
║     DeepSeek V3 + Suno API 集成系统                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    # 显示所有可用模板
    show_templates()

    print("\n" + "="*60)
    print("开始测试...")
    print("="*60)

    # 运行测试案例
    print("\n【测试1】灵感写歌模板")
    test_case_1_inspiration()

    input("\n按回车继续下一个测试...")

    print("\n【测试2】歌词改写模板")
    test_case_2_rewrite()

    input("\n按回车继续下一个测试...")

    print("\n【测试3】快速生成模板")
    test_case_3_quick()

    input("\n按回车继续下一个测试...")

    print("\n【测试4】情绪疗愈模板")
    test_case_4_healing()

    print("\n\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)
