"""
Suno AI 音乐创作 - 综合示例程序

演示如何使用 Suno 三大模块进行音乐创作：
1. 快速创作 - 从概念到成品
2. 专业制作 - 完整工作流
3. 批量创作 - 创作多首歌
4. 多风格改编 - 翻唱工作室
5. 音乐扩展 - 制作完整版

运行方式:
    python examples/suno_music_creator.py
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.clients import suno_generate, suno_extend, suno_cover


def print_separator(char="=", length=60):
    """打印分隔线"""
    print(char * length)


def print_header(text):
    """打印标题"""
    print_separator()
    print(f"  {text}")
    print_separator()


def scenario_1_quick_creation():
    """
    场景1：快速创作
    从一个主题快速生成一首完整的歌曲
    """
    print_header("场景1：快速创作 - 从概念到成品")

    # 创建输出目录
    output_dir = "outputs/scenario_1_quick_creation"
    os.makedirs(output_dir, exist_ok=True)

    # 定义创作主题
    theme = "夏日海滩的美好回忆"
    print(f"\n创作主题: {theme}")

    # 步骤1：快速生成（AI 自动创作歌词）
    print("\n[步骤1] 使用 AI 自动创作歌词并生成音乐...")
    task_id = suno_generate.quick_generate(
        prompt=f"写一首关于{theme}的轻快流行歌",
        model="V5",
        wait=False
    )
    print(f"✓ 任务已提交，任务ID: {task_id}")

    # 等待完成
    print("\n正在生成音乐，请稍候...")
    result = suno_generate.wait_for_completion(task_id, max_wait_time=300)

    if result.get('status') == 'completed':
        audio_data = result['data'][0]
        audio_id = audio_data['id']
        audio_url = audio_data.get('audio_url', '')
        video_url = audio_data.get('video_url', '')

        print("\n✓ 生成完成！")
        print(f"Audio ID: {audio_id}")
        print(f"音频链接: {audio_url}")
        print(f"视频链接: {video_url}")

        # 保存信息
        project_info = {
            "theme": theme,
            "task_id": task_id,
            "audio_id": audio_id,
            "audio_url": audio_url,
            "video_url": video_url,
            "model": "V5"
        }

        with open(f"{output_dir}/project_info.json", "w", encoding="utf-8") as f:
            json.dump(project_info, f, indent=2, ensure_ascii=False)

        print(f"\n项目信息已保存到: {output_dir}/project_info.json")
        return audio_id
    else:
        print(f"\n✗ 生成失败: {result.get('status')}")
        return None


def scenario_2_professional_production():
    """
    场景2：专业制作
    使用自定义歌词，完整的制作流程
    """
    print_header("场景2：专业制作 - 完整工作流")

    output_dir = "outputs/scenario_2_professional"
    os.makedirs(output_dir, exist_ok=True)

    # 步骤1：准备歌词
    print("\n[步骤1] 准备歌词...")
    lyrics = """
春风吹过田野
花儿开满山坡
蝴蝶在飞舞
歌声在回荡

温暖的阳光
洒在脸庞
这是春天的味道
这是希望的颜色

让我们一起歌唱
迎接新的希望
春天来了
带来无限可能
"""

    # 保存歌词
    with open(f"{output_dir}/lyrics.txt", "w", encoding="utf-8") as f:
        f.write(lyrics)
    print(f"✓ 歌词已保存到: {output_dir}/lyrics.txt")

    # 步骤2：生成原始版本
    print("\n[步骤2] 使用自定义歌词生成音乐...")
    gen_task = suno_generate.custom_generate(
        lyrics=lyrics,
        style="民谣，吉他伴奏，温暖人声",
        title="春天的田野",
        model="V5"
    )
    print(f"✓ 生成任务已提交: {gen_task}")

    print("\n正在生成，请稍候...")
    gen_result = suno_generate.wait_for_completion(gen_task, max_wait_time=300)

    if gen_result.get('status') == 'completed':
        audio_id = gen_result['data'][0]['id']
        audio_url = gen_result['data'][0].get('audio_url', '')

        print(f"\n✓ 原始版本生成完成")
        print(f"Audio ID: {audio_id}")

        # 步骤3：延长到完整版
        print("\n[步骤3] 延长到完整版本...")
        extend_task = suno_extend.simple_extend(
            audio_id=audio_id,
            model="V5",
            wait=False
        )
        print(f"✓ 延长任务已提交: {extend_task}")

        print("\n正在延长，请稍候...")
        extend_result = suno_extend.wait_for_completion(extend_task, max_wait_time=300)

        if extend_result.get('status') == 'completed':
            extended_audio_url = extend_result['data'][0].get('audio_url', '')
            print(f"\n✓ 延长完成")

            # 保存项目信息
            project_info = {
                "title": "春天的田野",
                "style": "民谣",
                "lyrics": lyrics,
                "original": {
                    "task_id": gen_task,
                    "audio_id": audio_id,
                    "audio_url": audio_url
                },
                "extended": {
                    "task_id": extend_task,
                    "audio_url": extended_audio_url
                }
            }

            with open(f"{output_dir}/project_info.json", "w", encoding="utf-8") as f:
                json.dump(project_info, f, indent=2, ensure_ascii=False)

            print(f"\n🎉 项目完成！")
            print(f"项目文件夹: {output_dir}")
            return audio_id
        else:
            print(f"\n✗ 延长失败: {extend_result.get('status')}")
    else:
        print(f"\n✗ 生成失败: {gen_result.get('status')}")

    return None


def scenario_3_batch_creation():
    """
    场景3：批量创作
    一次创作多首歌曲（四季主题）
    """
    print_header("场景3：批量创作 - 四季主题")

    output_dir = "outputs/scenario_3_batch"
    os.makedirs(output_dir, exist_ok=True)

    # 定义四季主题
    themes = [
        {
            "season": "春",
            "prompt": "春天花园，鸟语花香，万物复苏",
            "style": "民谣，吉他伴奏",
            "mood": "温暖、希望"
        },
        {
            "season": "夏",
            "prompt": "夏日海滩，阳光沙滩，海浪声",
            "style": "清新流行",
            "mood": "活力、欢快"
        },
        {
            "season": "秋",
            "prompt": "秋天落叶，金黄色调，收获季节",
            "style": "古风，琵琶伴奏",
            "mood": "宁静、怀旧"
        },
        {
            "season": "冬",
            "prompt": "冬日雪景，白雪皑皑，温暖炉火",
            "style": "钢琴独奏",
            "mood": "温馨、平静"
        }
    ]

    tasks_info = []

    print(f"\n准备创作 {len(themes)} 首歌曲...")

    for idx, theme in enumerate(themes, 1):
        print(f"\n[{idx}/{len(themes)}] 创作《{theme['season']}》")
        print(f"风格: {theme['style']}")
        print(f"情绪: {theme['mood']}")

        try:
            # 提交任务
            task_id = suno_generate.quick_generate(
                prompt=f"写一首关于{theme['prompt']}的歌，风格：{theme['style']}，情绪：{theme['mood']}",
                model="V5",
                wait=False
            )

            tasks_info.append({
                "season": theme['season'],
                "task_id": task_id,
                "style": theme['style'],
                "mood": theme['mood'],
                "status": "submitted"
            })

            print(f"✓ 任务已提交: {task_id}")

            # 短暂延迟，避免过快提交
            time.sleep(2)

        except Exception as e:
            print(f"✗ 提交失败: {e}")

    # 保存任务列表
    with open(f"{output_dir}/batch_tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks_info, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 已提交 {len(tasks_info)} 个任务")
    print(f"任务列表已保存到: {output_dir}/batch_tasks.json")
    print("\n提示：稍后可以使用以下代码查询所有任务状态：")
    print("""
    import json
    from modules.clients import suno_generate

    with open("outputs/scenario_3_batch/batch_tasks.json") as f:
        tasks = json.load(f)

    for task in tasks:
        status = suno_generate.get_task_status(task['task_id'])
        print(f"{task['season']}: {status.get('status')}")
    """)


def scenario_4_remix_studio():
    """
    场景4：多风格改编
    将同一首歌改编成多种风格（需要先有音频文件）
    """
    print_header("场景4：多风格改编 - 翻唱工作室")

    output_dir = "outputs/scenario_4_remix"
    os.makedirs(output_dir, exist_ok=True)

    print("\n⚠️  此场景需要先准备一个音频文件（≤2分钟）")
    print("请将音频文件放在项目根目录，命名为 'original_song.mp3'")

    # 检查文件是否存在
    original_file = "original_song.mp3"
    if not os.path.exists(original_file):
        print(f"\n✗ 未找到文件: {original_file}")
        print("\n演示代码（实际使用时取消注释）：")
        print("""
from modules.clients import suno_cover

# 定义多种风格
cover_styles = [
    {"name": "EDM Remix", "style": "电子舞曲，强劲节奏，适合夜店"},
    {"name": "Acoustic", "style": "声学版本，吉他伴奏，温暖人声"},
    {"name": "Jazz", "style": "爵士风格，萨克斯主导，慵懒节奏"},
    {"name": "Lo-fi", "style": "lo-fi hip hop，慵懒节奏，适合学习"}
]

# 批量提交翻唱任务
remix_tasks = []
for style_info in cover_styles:
    task_id = suno_cover.cover_from_file(
        file_path="original_song.mp3",
        style=style_info['style'],
        title=f"My Song - {style_info['name']}",
        model="V5"
    )
    remix_tasks.append({
        "name": style_info['name'],
        "task_id": task_id
    })
    print(f"✓ {style_info['name']} 已提交")

# 保存任务信息
import json
with open("outputs/scenario_4_remix/remix_tasks.json", "w") as f:
    json.dump(remix_tasks, f, indent=2, ensure_ascii=False)
""")
        return

    # 如果文件存在，执行翻唱
    print(f"\n✓ 找到文件: {original_file}")

    cover_styles = [
        {"name": "EDM Remix", "style": "电子舞曲，强劲节奏"},
        {"name": "Acoustic Version", "style": "声学版本，吉他伴奏"},
        {"name": "Jazz Version", "style": "爵士风格，萨克斯主导"}
    ]

    remix_tasks = []
    for idx, style_info in enumerate(cover_styles, 1):
        print(f"\n[{idx}/{len(cover_styles)}] 创作 {style_info['name']}")

        try:
            task_id = suno_cover.cover_from_file(
                file_path=original_file,
                style=style_info['style'],
                title=f"Original - {style_info['name']}",
                model="V5"
            )

            remix_tasks.append({
                "name": style_info['name'],
                "style": style_info['style'],
                "task_id": task_id
            })

            print(f"✓ 任务已提交: {task_id}")
            time.sleep(2)

        except Exception as e:
            print(f"✗ 提交失败: {e}")

    # 保存任务信息
    with open(f"{output_dir}/remix_tasks.json", "w", encoding="utf-8") as f:
        json.dump(remix_tasks, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 已提交 {len(remix_tasks)} 个翻唱任务")
    print(f"任务信息已保存到: {output_dir}/remix_tasks.json")


def scenario_5_extend_music():
    """
    场景5：音乐扩展
    演示如何将短音乐扩展到更长版本
    """
    print_header("场景5：音乐扩展 - 制作完整版")

    output_dir = "outputs/scenario_5_extend"
    os.makedirs(output_dir, exist_ok=True)

    print("\n此场景演示音乐扩展功能")
    print("需要先生成一首短音乐，然后延长到完整版\n")

    # 步骤1：生成短版本
    print("[步骤1] 生成短版本音乐...")
    gen_task = suno_generate.quick_generate(
        prompt="一首轻快的钢琴曲，适合下午茶",
        model="V5",
        wait=False
    )
    print(f"✓ 生成任务已提交: {gen_task}")

    print("\n正在生成，请稍候...")
    gen_result = suno_generate.wait_for_completion(gen_task, max_wait_time=300)

    if gen_result.get('status') != 'completed':
        print(f"\n✗ 生成失败: {gen_result.get('status')}")
        return

    audio_id = gen_result['data'][0]['id']
    original_url = gen_result['data'][0].get('audio_url', '')
    print(f"\n✓ 短版本生成完成")
    print(f"Audio ID: {audio_id}")

    # 步骤2：简单扩展（使用原参数）
    print("\n[步骤2] 简单扩展（保持原风格）...")
    simple_task = suno_extend.simple_extend(
        audio_id=audio_id,
        model="V5",
        wait=False
    )
    print(f"✓ 简单扩展任务已提交: {simple_task}")

    # 步骤3：自定义扩展（从特定位置）
    print("\n[步骤3] 自定义扩展（从特定位置开始）...")
    custom_task = suno_extend.custom_extend(
        audio_id=audio_id,
        continue_at=60,  # 从60秒处开始
        style="轻快钢琴，逐渐增强节奏",
        title="Afternoon Tea (Extended)",
        prompt="继续之前的轻快旋律，逐渐增加钢琴的力度",
        model="V5"
    )
    print(f"✓ 自定义扩展任务已提交: {custom_task}")

    # 保存信息
    extend_info = {
        "original": {
            "task_id": gen_task,
            "audio_id": audio_id,
            "audio_url": original_url
        },
        "simple_extend": {
            "task_id": simple_task,
            "description": "使用原参数延长"
        },
        "custom_extend": {
            "task_id": custom_task,
            "continue_at": 60,
            "description": "从60秒处自定义延长"
        }
    }

    with open(f"{output_dir}/extend_info.json", "w", encoding="utf-8") as f:
        json.dump(extend_info, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 扩展任务已提交")
    print(f"信息已保存到: {output_dir}/extend_info.json")
    print("\n提示：可以稍后查询任务状态：")
    print(f"  简单扩展: suno_extend.get_task_status('{simple_task}')")
    print(f"  自定义扩展: suno_extend.get_task_status('{custom_task}')")


def show_menu():
    """显示主菜单"""
    print_separator("=", 70)
    print("  Suno AI 音乐创作 - 综合示例程序")
    print_separator("=", 70)
    print("\n选择一个场景：\n")
    print("  1. 快速创作 - 从概念到成品（最简单）")
    print("  2. 专业制作 - 完整工作流（推荐）")
    print("  3. 批量创作 - 创作多首歌（四季主题）")
    print("  4. 多风格改编 - 翻唱工作室（需要音频文件）")
    print("  5. 音乐扩展 - 制作完整版")
    print("\n  0. 退出")
    print_separator("=", 70)


def main():
    """主程序"""
    # 确保输出目录存在
    os.makedirs("outputs", exist_ok=True)

    while True:
        show_menu()

        try:
            choice = input("\n请选择场景 (0-5): ").strip()

            if choice == "0":
                print("\n感谢使用！再见 👋")
                break

            elif choice == "1":
                scenario_1_quick_creation()

            elif choice == "2":
                scenario_2_professional_production()

            elif choice == "3":
                scenario_3_batch_creation()

            elif choice == "4":
                scenario_4_remix_studio()

            elif choice == "5":
                scenario_5_extend_music()

            else:
                print("\n⚠️  无效选择，请输入 0-5")
                continue

            # 询问是否继续
            print("\n" + "=" * 70)
            continue_choice = input("\n是否继续体验其他场景？(y/n): ").strip().lower()
            if continue_choice != 'y':
                print("\n感谢使用！再见 👋")
                break

        except KeyboardInterrupt:
            print("\n\n程序已中断，再见 👋")
            break
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            print("请检查 API Key 配置和网络连接")

            continue_choice = input("\n是否继续？(y/n): ").strip().lower()
            if continue_choice != 'y':
                break


if __name__ == "__main__":
    print("\n欢迎使用 Suno AI 音乐创作综合示例！\n")

    # 检查 API Key
    api_key = os.getenv("SUNO_API_KEY")
    if not api_key:
        # 尝试从 config.json 读取
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    api_key = config.get("suno", {}).get("api_key")
            except Exception:
                pass

    if not api_key:
        print("⚠️  警告：未检测到 SUNO_API_KEY")
        print("\n请先配置 API Key：")
        print("  方式1：set SUNO_API_KEY=your_key  (Windows)")
        print("  方式2：在 config.json 中配置")
        print("\n详见文档: docs/Suno快速入门-5分钟上手.md\n")

        proceed = input("是否继续（某些功能可能无法使用）？(y/n): ").strip().lower()
        if proceed != 'y':
            sys.exit(0)

    main()
