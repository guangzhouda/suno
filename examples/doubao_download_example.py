"""
豆包资源下载完整示例

演示如何下载生成的图片和视频到本地。

重要说明：
1. 图片生成后会返回URL，图片会在豆包服务器上保存一段时间（通常14-30天）
2. 视频生成是异步任务，提交后需要等待处理完成
3. 建议立即下载生成的资源到本地，避免URL过期

使用前准备：
- 设置环境变量 ARK_API_KEY
- 确保网络连接正常
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.clients import doubao_text
from modules.clients import doubao_image
from modules.clients import doubao_vision
from modules.clients import doubao_video
from modules.clients import doubao_downloader


def example_1_download_image():
    """示例1：生成图片并下载"""
    print("\n" + "="*60)
    print("示例1：生成专辑封面并下载到本地")
    print("="*60 + "\n")

    try:
        # 步骤1：生成图片
        print("步骤1：生成专辑封面...")
        result = doubao_image.generate_album_cover(
            title="夏日回忆",
            artist="AI音乐人",
            style="清新流行",
            mood="温暖怀旧",
            color_scheme="暖色调",
            elements="海边、夕阳",
            size="1K"
        )

        print(f"✓ 封面生成成功！")
        print(f"  URL: {result['url']}")

        # 步骤2：下载图片到本地
        print("\n步骤2：下载图片到本地...")
        file_path = doubao_downloader.download_image(
            url=result['url'],
            save_dir="outputs/album_covers",
            filename="summer_memories_cover.jpg"
        )

        # 步骤3：查看文件信息
        print("\n步骤3：查看文件信息...")
        info = doubao_downloader.get_file_info(file_path)
        print(f"  文件名: {info['filename']}")
        print(f"  大小: {info['size_mb']:.2f} MB")
        print(f"  完整路径: {info['path']}")

        print(f"\n✓ 图片已保存到本地: {file_path}")
        print(f"  可以使用图片查看器打开该文件")

        return file_path

    except Exception as e:
        print(f"✗ 失败: {e}")
        return None


def example_2_batch_download():
    """示例2：批量生成和下载图片"""
    print("\n" + "="*60)
    print("示例2：批量生成专辑封面并下载")
    print("="*60 + "\n")

    try:
        # 定义多个封面配置
        covers = [
            {"title": "春天", "mood": "清新", "elements": "花朵、绿叶"},
            {"title": "夏天", "mood": "热情", "elements": "海滩、阳光"},
            {"title": "秋天", "mood": "温暖", "elements": "落叶、夕阳"},
            {"title": "冬天", "mood": "宁静", "elements": "雪花、冰晶"}
        ]

        image_urls = []

        # 生成所有封面
        print("正在生成封面...")
        for idx, config in enumerate(covers, 1):
            print(f"\n[{idx}/{len(covers)}] 生成《{config['title']}》封面...")
            result = doubao_image.generate_album_cover(
                title=config['title'],
                style="艺术插画",
                mood=config['mood'],
                elements=config['elements'],
                size="1K"
            )
            image_urls.append(result['url'])
            print(f"  ✓ URL: {result['url']}")

        # 批量下载
        print("\n\n开始批量下载...")
        file_paths = doubao_downloader.batch_download_images(
            urls=image_urls,
            save_dir="outputs/seasons_covers",
            prefix="season"
        )

        print(f"\n✓ 批量下载完成！共 {len([p for p in file_paths if p])} 张图片")
        return file_paths

    except Exception as e:
        print(f"✗ 失败: {e}")
        return None


def example_3_download_with_lyrics():
    """示例3：根据歌词生成封面并下载"""
    print("\n" + "="*60)
    print("示例3：根据歌词生成封面并下载")
    print("="*60 + "\n")

    try:
        # 步骤1：生成歌词
        print("步骤1：生成歌词...")
        lyrics = doubao_text.generate_lyrics(
            prompt="海边的夕阳和回忆",
            style="民谣",
            mood="怀旧",
            temperature=0.8
        )
        print(f"✓ 歌词生成完成（{len(lyrics)}字）")
        print(f"\n歌词节选：\n{lyrics[:200]}...\n")

        # 步骤2：根据歌词生成封面
        print("步骤2：根据歌词生成封面...")
        result = doubao_image.generate_cover_from_lyrics(
            lyrics=lyrics,
            style="民谣",
            size="1K"
        )
        print(f"✓ 封面生成成功")
        print(f"  URL: {result['url']}")

        # 步骤3：下载封面
        print("\n步骤3：下载封面...")
        file_path = doubao_downloader.download_image(
            url=result['url'],
            save_dir="outputs/lyrics_covers",
            filename="folk_song_cover.jpg"
        )

        print(f"\n✓ 完成！文件保存在: {file_path}")
        return file_path

    except Exception as e:
        print(f"✗ 失败: {e}")
        return None


def example_4_video_generation_guide():
    """示例4：视频生成和获取指南"""
    print("\n" + "="*60)
    print("示例4：视频生成和下载说明")
    print("="*60 + "\n")

    print("""
视频生成说明：
============

1. 视频生成是异步任务
   - 提交任务后会立即返回 task_id
   - 实际生成需要几分钟到十几分钟
   - 需要通过 task_id 查询任务状态

2. 当前限制
   - 豆包API可能不提供公开的任务查询接口
   - 建议使用豆包官方控制台查看任务状态
   - 或联系豆包技术支持获取查询方法

3. 替代方案
   - 使用豆包Web控制台：https://console.volcengine.com/
   - 在控制台的"内容生成"页面查看任务状态
   - 任务完成后可以在控制台下载视频

4. 代码示例（提交任务）
    """)

    try:
        print("\n正在提交视频生成任务...")

        result = doubao_video.text_to_video(
            prompt="一个女孩站在海边看夕阳，海风吹动她的头发",
            ratio="16:9",
            duration=5
        )

        print(f"\n✓ 任务提交成功！")
        print(f"  任务ID: {result['task_id']}")
        print(f"  状态: {result['status']}")
        print(f"  提示词: {result['prompt']}")

        print(f"\n后续步骤：")
        print(f"1. 记录任务ID: {result['task_id']}")
        print(f"2. 访问豆包控制台: https://console.volcengine.com/")
        print(f"3. 在"内容生成"页面查找该任务ID")
        print(f"4. 等待任务完成后下载视频")

        # 如果有查询接口，可以使用以下代码（需要API支持）
        print(f"\n如果有查询接口，可以使用：")
        print(f"```python")
        print(f"# 查询任务状态")
        print(f"status = doubao_downloader.query_video_task('{result['task_id']}')")
        print(f"")
        print(f"# 等待完成并下载")
        print(f"video_path = doubao_downloader.wait_for_video(")
        print(f"    task_id='{result['task_id']}',")
        print(f"    save_dir='outputs/videos',")
        print(f"    max_wait_time=600")
        print(f")")
        print(f"```")

        return result

    except Exception as e:
        print(f"✗ 提交失败: {e}")
        return None


def example_5_complete_workflow_with_download():
    """示例5：完整工作流（包含下载）"""
    print("\n" + "="*60)
    print("示例5：完整音乐创作流程（生成+下载）")
    print("="*60 + "\n")

    try:
        # 步骤1：分析图片
        print("步骤1：分析图片...")
        test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
        music_elements = doubao_vision.image_to_music_prompt(test_image_url)
        print(f"✓ 分析完成")
        print(f"  推荐风格: {music_elements['style']}")
        print(f"  推荐情绪: {music_elements['emotion']}")

        # 步骤2：生成歌词
        print("\n步骤2：生成歌词...")
        lyrics = doubao_text.generate_lyrics(
            prompt=f"基于{music_elements['scene']}场景",
            style=music_elements['style'],
            mood=music_elements['emotion'],
            temperature=0.8
        )
        print(f"✓ 歌词生成完成（{len(lyrics)}字）")

        # 步骤3：生成封面
        print("\n步骤3：生成专辑封面...")
        cover_result = doubao_image.generate_album_cover(
            title="AI创作",
            style=music_elements['style'],
            mood=music_elements['emotion'],
            color_scheme=music_elements['color_tone'],
            size="1K"
        )
        print(f"✓ 封面生成成功")

        # 步骤4：下载封面
        print("\n步骤4：下载封面到本地...")
        cover_path = doubao_downloader.download_image(
            url=cover_result['url'],
            save_dir="outputs/complete_works",
            filename="ai_music_cover.jpg"
        )
        print(f"✓ 封面已保存: {cover_path}")

        # 步骤5：保存歌词
        print("\n步骤5：保存歌词到文件...")
        lyrics_path = os.path.join("outputs/complete_works", "ai_music_lyrics.txt")
        os.makedirs(os.path.dirname(lyrics_path), exist_ok=True)
        with open(lyrics_path, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"✓ 歌词已保存: {lyrics_path}")

        # 步骤6：提交MV生成任务
        print("\n步骤6：提交MV生成任务...")
        mv_result = doubao_video.generate_mv(
            lyrics=lyrics,
            style=music_elements['style'],
            mood=music_elements['emotion'],
            cover_image_url=cover_result['url'],
            ratio="16:9"
        )
        print(f"✓ MV任务提交成功")
        print(f"  任务ID: {mv_result['task_id']}")

        # 总结
        print("\n" + "="*60)
        print("完整音乐作品创作完成！")
        print("="*60)
        print(f"\n已保存的文件：")
        print(f"  📝 歌词: {lyrics_path}")
        print(f"  🎨 封面: {cover_path}")
        print(f"  🎬 MV任务ID: {mv_result['task_id']}")
        print(f"\n请访问豆包控制台查看MV生成进度：")
        print(f"https://console.volcengine.com/")

        return {
            "lyrics_path": lyrics_path,
            "cover_path": cover_path,
            "mv_task_id": mv_result['task_id']
        }

    except Exception as e:
        print(f"✗ 失败: {e}")
        return None


def example_6_download_existing_image():
    """示例6：下载已有的图片URL"""
    print("\n" + "="*60)
    print("示例6：下载已有的图片URL")
    print("="*60 + "\n")

    print("如果你已经有图片URL（之前生成的），可以直接下载：\n")

    # 示例URL（替换成你自己的）
    example_url = "https://example.com/your_generated_image.jpg"

    print(f"使用示例：")
    print(f"```python")
    print(f"from modules.clients import doubao_downloader")
    print(f"")
    print(f"# 下载图片")
    print(f"file_path = doubao_downloader.download_image(")
    print(f"    url='{example_url}',")
    print(f"    save_dir='outputs/my_images',")
    print(f"    filename='my_cover.jpg'")
    print(f")")
    print(f"```")

    print(f"\n提示：")
    print(f"1. 图片URL通常在生成时返回")
    print(f"2. URL有效期通常为14-30天")
    print(f"3. 建议生成后立即下载保存")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("豆包资源下载示例")
    print("="*60)

    print("\n请选择要运行的示例：")
    print("1. 生成并下载单张封面")
    print("2. 批量生成和下载封面")
    print("3. 根据歌词生成封面并下载")
    print("4. 视频生成和下载说明")
    print("5. 完整工作流（生成+下载）")
    print("6. 下载已有图片URL的说明")
    print("0. 运行所有示例")

    try:
        choice = input("\n请输入选项（0-6）：").strip()

        if choice == "1":
            example_1_download_image()
        elif choice == "2":
            example_2_batch_download()
        elif choice == "3":
            example_3_download_with_lyrics()
        elif choice == "4":
            example_4_video_generation_guide()
        elif choice == "5":
            example_5_complete_workflow_with_download()
        elif choice == "6":
            example_6_download_existing_image()
        elif choice == "0":
            # 运行所有示例
            example_1_download_image()
            example_2_batch_download()
            example_3_download_with_lyrics()
            example_4_video_generation_guide()
            example_5_complete_workflow_with_download()
            example_6_download_existing_image()
        else:
            print("无效的选项！")

    except KeyboardInterrupt:
        print("\n\n程序已退出。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")


if __name__ == "__main__":
    main()
