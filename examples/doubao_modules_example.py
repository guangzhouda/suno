"""
豆包AI模块集成示例

演示如何使用四个独立的豆包模块完成音乐创作全流程：
1. doubao_text.py - 生成歌词
2. doubao_image.py - 生成专辑封面
3. doubao_vision.py - 分析图片并提取音乐元素（图片成歌）
4. doubao_video.py - 生成音乐MV

使用前准备：
1. 安装依赖: pip install volcengine-python-sdk[ark]
2. 设置API Key:
   - Windows: set ARK_API_KEY=your_api_key
   - Linux/Mac: export ARK_API_KEY=your_api_key
   或在 config.json 中配置
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.clients import doubao_text
from modules.clients import doubao_image
from modules.clients import doubao_vision
from modules.clients import doubao_video


def example_1_generate_lyrics():
    """示例1：生成歌词"""
    print("\n" + "="*60)
    print("示例1：使用 doubao_text 生成歌词")
    print("="*60 + "\n")

    try:
        # 快速生成歌词
        lyrics = doubao_text.generate_lyrics(
            prompt="夏日午后的咖啡馆，窗外阳光洒进来",
            style="轻音乐",
            mood="慵懒放松",
            theme="都市慢生活",
            temperature=0.8
        )

        print("生成的歌词：\n")
        print(lyrics)
        print("\n✓ 歌词生成成功！")

        return lyrics

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        return None


def example_2_generate_album_cover():
    """示例2：生成专辑封面"""
    print("\n" + "="*60)
    print("示例2：使用 doubao_image 生成专辑封面")
    print("="*60 + "\n")

    try:
        # 生成专辑封面
        result = doubao_image.generate_album_cover(
            title="夏日咖啡馆",
            artist="AI音乐人",
            style="轻音乐",
            mood="慵懒放松",
            color_scheme="暖色调",
            elements="咖啡、阳光、窗户、午后",
            size="1K",
            watermark=False
        )

        print(f"封面图片URL: {result['url']}")
        print(f"图片尺寸: {result['size']}")
        print(f"生成提示词: {result['prompt']}")
        print("\n✓ 封面生成成功！")

        return result['url']

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        return None


def example_3_image_to_song():
    """示例3：图片成歌（分析图片提取音乐元素）"""
    print("\n" + "="*60)
    print("示例3：使用 doubao_vision 分析图片并提取音乐元素")
    print("="*60 + "\n")

    try:
        # 测试图片URL（可以替换成你自己的图片）
        test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"

        # 方式1：提取音乐元素
        print("正在分析图片...")
        music_elements = doubao_vision.image_to_music_prompt(test_image_url)

        print("\n分析结果：")
        print(f"  场景: {music_elements['scene']}")
        print(f"  情绪: {music_elements['emotion']}")
        print(f"  色调: {music_elements['color_tone']}")
        print(f"  推荐风格: {music_elements['style']}")
        print(f"  推荐乐器: {music_elements['instruments']}")
        print(f"  节奏: {music_elements['tempo']}")
        print(f"  氛围: {music_elements['atmosphere']}")

        # 方式2：生成歌词创作提示
        print("\n正在生成歌词创作提示...")
        lyrics_prompt = doubao_vision.image_to_lyrics_prompt(test_image_url)
        print(f"\n歌词创作提示：\n{lyrics_prompt}")

        print("\n✓ 图片分析成功！")

        return music_elements

    except Exception as e:
        print(f"✗ 分析失败: {e}")
        return None


def example_4_generate_mv():
    """示例4：生成音乐MV"""
    print("\n" + "="*60)
    print("示例4：使用 doubao_video 生成音乐MV")
    print("="*60 + "\n")

    try:
        # 示例歌词
        lyrics = """
        [Verse 1]
        阳光洒进咖啡馆的窗
        午后时光慵懒又温暖
        一杯拿铁的香气飘散
        翻开书页感受这份闲
        """

        # 生成MV
        print("正在提交视频生成任务...")
        result = doubao_video.generate_mv(
            lyrics=lyrics,
            style="轻音乐",
            scene="咖啡馆内景",
            mood="慵懒放松",
            ratio="16:9",
            duration=5
        )

        print(f"\n任务ID: {result['task_id']}")
        print(f"状态: {result['status']}")
        print(f"视频比例: {result['ratio']}")
        print(f"时长: {result['duration']}秒")
        print(f"生成提示词: {result['prompt']}")

        print("\n✓ MV生成任务提交成功！")
        print("注意：视频生成是异步任务，需要等待一段时间后查询结果")

        return result

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        return None


def example_5_complete_workflow():
    """示例5：完整工作流 - 从图片到完整音乐作品"""
    print("\n" + "="*60)
    print("示例5：完整工作流 - 图片 → 歌词 → 封面 → MV")
    print("="*60 + "\n")

    try:
        # 步骤1：分析图片
        print("步骤1：分析图片，提取音乐元素...")
        test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
        music_elements = doubao_vision.image_to_music_prompt(test_image_url)
        print(f"  ✓ 推荐风格: {music_elements['style']}")
        print(f"  ✓ 推荐情绪: {music_elements['emotion']}")

        # 步骤2：根据图片分析结果生成歌词
        print("\n步骤2：根据分析结果生成歌词...")
        lyrics_prompt = f"""
        根据以下元素创作一首歌：
        场景：{music_elements['scene']}
        情绪：{music_elements['emotion']}
        氛围：{music_elements['atmosphere']}
        """
        lyrics = doubao_text.generate_lyrics(
            prompt=lyrics_prompt,
            style=music_elements['style'],
            mood=music_elements['emotion'],
            temperature=0.8
        )
        print(f"  ✓ 歌词生成完成（{len(lyrics)}字）")

        # 步骤3：生成专辑封面
        print("\n步骤3：生成专辑封面...")
        cover_result = doubao_image.generate_album_cover(
            title="AI创作",
            style=music_elements['style'],
            mood=music_elements['emotion'],
            color_scheme=music_elements['color_tone'],
            elements=music_elements.get('keywords', ''),
            size="1K"
        )
        print(f"  ✓ 封面URL: {cover_result['url']}")

        # 步骤4：生成MV（使用刚生成的封面作为首帧）
        print("\n步骤4：生成音乐MV...")
        mv_result = doubao_video.generate_mv(
            lyrics=lyrics,
            style=music_elements['style'],
            mood=music_elements['emotion'],
            cover_image_url=cover_result['url'],
            ratio="16:9",
            duration=5
        )
        print(f"  ✓ MV任务ID: {mv_result['task_id']}")

        # 输出完整结果
        print("\n" + "="*60)
        print("完整音乐作品创作完成！")
        print("="*60)
        print(f"\n📝 歌词（节选）：\n{lyrics[:200]}...")
        print(f"\n🎨 封面图片：{cover_result['url']}")
        print(f"\n🎬 MV任务ID：{mv_result['task_id']}")
        print("\n所有资源都已生成！")

        return {
            "lyrics": lyrics,
            "cover_url": cover_result['url'],
            "mv_task_id": mv_result['task_id'],
            "music_elements": music_elements
        }

    except Exception as e:
        print(f"✗ 工作流执行失败: {e}")
        return None


def example_6_text_to_video():
    """示例6：纯文生视频"""
    print("\n" + "="*60)
    print("示例6：使用 doubao_video 纯文生视频")
    print("="*60 + "\n")

    try:
        # 文生视频
        result = doubao_video.text_to_video(
            prompt="一个女孩站在海边看夕阳，海风吹动她的头发，镜头缓缓拉远，展现整个海岸线",
            ratio="16:9",
            duration=5
        )

        print(f"任务ID: {result['task_id']}")
        print(f"提示词: {result['prompt']}")
        print("\n✓ 视频生成任务提交成功！")

        return result

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        return None


def example_7_chat_with_ai():
    """示例7：与AI对话（用于歌词创作讨论）"""
    print("\n" + "="*60)
    print("示例7：使用 doubao_text 与AI对话")
    print("="*60 + "\n")

    try:
        # 多轮对话示例
        messages = [
            {"role": "system", "content": "你是一位专业的词曲作者，擅长各种风格的歌词创作。"},
            {"role": "user", "content": "我想写一首关于友情的歌，但不知道从哪里开始。"}
        ]

        response = doubao_text.chat(
            messages=messages,
            temperature=0.7
        )

        print("AI回复：")
        print(response)
        print("\n✓ 对话成功！")

        return response

    except Exception as e:
        print(f"✗ 对话失败: {e}")
        return None


def main():
    """主函数：运行所有示例"""
    print("\n" + "="*60)
    print("豆包AI模块集成示例")
    print("="*60)

    print("\n请选择要运行的示例：")
    print("1. 生成歌词")
    print("2. 生成专辑封面")
    print("3. 图片成歌（分析图片提取音乐元素）")
    print("4. 生成音乐MV")
    print("5. 完整工作流（图片→歌词→封面→MV）")
    print("6. 纯文生视频")
    print("7. 与AI对话（歌词创作讨论）")
    print("0. 运行所有示例")

    try:
        choice = input("\n请输入选项（0-7）：").strip()

        if choice == "1":
            example_1_generate_lyrics()
        elif choice == "2":
            example_2_generate_album_cover()
        elif choice == "3":
            example_3_image_to_song()
        elif choice == "4":
            example_4_generate_mv()
        elif choice == "5":
            example_5_complete_workflow()
        elif choice == "6":
            example_6_text_to_video()
        elif choice == "7":
            example_7_chat_with_ai()
        elif choice == "0":
            # 运行所有示例
            example_1_generate_lyrics()
            example_2_generate_album_cover()
            example_3_image_to_song()
            example_4_generate_mv()
            example_6_text_to_video()
            example_7_chat_with_ai()
            # 最后运行完整工作流
            example_5_complete_workflow()
        else:
            print("无效的选项！")

    except KeyboardInterrupt:
        print("\n\n程序已退出。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")


if __name__ == "__main__":
    main()
