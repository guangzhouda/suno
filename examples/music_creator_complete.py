"""
豆包AI音乐创作完整示例

综合使用五个模块创作完整的音乐作品：
- doubao_text: 歌词生成
- doubao_image: 封面生成
- doubao_vision: 图片分析
- doubao_video: MV生成
- doubao_downloader: 资源下载

场景1: 快速创作 - 主题 → 歌词 + 封面
场景2: 图片成歌 - 图片 → 分析 → 歌词 → 封面 → MV
场景3: 完整制作 - 从创意到成品的全流程
场景4: 批量创作 - 一次创作多首歌曲
场景5: 交互式创作 - 根据用户反馈迭代优化

使用前准备：
1. pip install volcengine-python-sdk[ark]
2. set ARK_API_KEY=your_key (Windows) 或 export ARK_API_KEY=your_key (Linux/Mac)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.clients import doubao_text
from modules.clients import doubao_image
from modules.clients import doubao_vision
from modules.clients import doubao_video
from modules.clients import doubao_downloader


# ============================================================
# 工具函数
# ============================================================

def print_header(title):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_step(step_num, description):
    """打印步骤"""
    print(f"\n【步骤 {step_num}】{description}")
    print("-" * 70)


def save_project_info(project_dir, info):
    """保存项目信息到JSON"""
    info_file = Path(project_dir) / "project_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 项目信息已保存: {info_file}")


def create_project_folder(base_dir="outputs/projects"):
    """创建项目文件夹"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir = Path(base_dir) / f"music_{timestamp}"
    project_dir.mkdir(parents=True, exist_ok=True)
    return str(project_dir)


# ============================================================
# 场景1: 快速创作（主题 → 歌词 + 封面）
# ============================================================

def scenario_1_quick_creation():
    """场景1: 快速创作一首歌曲"""
    print_header("场景1: 快速创作 - 主题到成品")

    # 创建项目文件夹
    project_dir = create_project_folder()
    print(f"📁 项目文件夹: {project_dir}\n")

    # 定义创作主题
    theme = "夏日海边的回忆"
    style = "清新流行"
    mood = "温暖怀旧"

    print(f"🎵 创作主题: {theme}")
    print(f"🎨 音乐风格: {style}")
    print(f"💭 情绪氛围: {mood}")

    project_info = {
        "theme": theme,
        "style": style,
        "mood": mood,
        "created_at": datetime.now().isoformat()
    }

    try:
        # 步骤1: 生成歌词
        print_step(1, "生成歌词")
        lyrics = doubao_text.generate_lyrics(
            prompt=theme,
            style=style,
            mood=mood,
            temperature=0.8
        )
        print(f"✓ 歌词生成成功 ({len(lyrics)}字)")
        print(f"\n歌词预览:\n{lyrics[:300]}...\n")

        # 保存歌词
        lyrics_file = Path(project_dir) / "lyrics.txt"
        with open(lyrics_file, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"  ✓ 歌词已保存: {lyrics_file}")
        project_info['lyrics_file'] = str(lyrics_file)

        # 步骤2: 生成专辑封面
        print_step(2, "生成专辑封面")
        cover_result = doubao_image.generate_album_cover(
            title=theme,
            style=style,
            mood=mood,
            color_scheme="暖色调",
            elements="海边、夕阳、回忆",
            size="1K"
        )
        print(f"✓ 封面生成成功")
        print(f"  URL: {cover_result['url']}")
        project_info['cover_url'] = cover_result['url']

        # 步骤3: 下载封面
        print_step(3, "下载封面到本地")
        cover_file = doubao_downloader.download_image(
            url=cover_result['url'],
            save_dir=project_dir,
            filename="cover.jpg"
        )
        print(f"✓ 封面已保存: {cover_file}")
        project_info['cover_file'] = cover_file

        # 保存项目信息
        save_project_info(project_dir, project_info)

        # 总结
        print_header("场景1 完成！")
        print(f"✓ 歌词: {lyrics_file}")
        print(f"✓ 封面: {cover_file}")
        print(f"✓ 项目文件夹: {project_dir}")

        return project_info

    except Exception as e:
        print(f"\n✗ 创作失败: {e}")
        return None


# ============================================================
# 场景2: 图片成歌（图片 → 分析 → 歌词 → 封面 → MV）
# ============================================================

def scenario_2_image_to_song():
    """场景2: 从一张图片创作完整音乐作品"""
    print_header("场景2: 图片成歌 - 完整创作流程")

    # 创建项目文件夹
    project_dir = create_project_folder()
    print(f"📁 项目文件夹: {project_dir}\n")

    # 使用测试图片（你可以替换成自己的图片URL）
    image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
    print(f"📸 输入图片: {image_url}")

    project_info = {
        "source_image_url": image_url,
        "created_at": datetime.now().isoformat()
    }

    try:
        # 步骤1: 分析图片，提取音乐元素
        print_step(1, "分析图片，提取音乐元素")
        music_elements = doubao_vision.image_to_music_prompt(image_url)

        print(f"✓ 图片分析完成:")
        print(f"  场景: {music_elements['scene']}")
        print(f"  情绪: {music_elements['emotion']}")
        print(f"  色调: {music_elements['color_tone']}")
        print(f"  推荐风格: {music_elements['style']}")
        print(f"  推荐乐器: {music_elements['instruments']}")
        print(f"  推荐节奏: {music_elements['tempo']}")

        project_info['music_elements'] = music_elements

        # 步骤2: 根据分析结果生成歌词
        print_step(2, "根据图片分析生成歌词")
        lyrics = doubao_text.generate_lyrics(
            prompt=f"基于{music_elements['scene']}场景创作",
            style=music_elements['style'],
            mood=music_elements['emotion'],
            temperature=0.8
        )
        print(f"✓ 歌词生成成功 ({len(lyrics)}字)")
        print(f"\n歌词预览:\n{lyrics[:300]}...\n")

        # 保存歌词
        lyrics_file = Path(project_dir) / "lyrics.txt"
        with open(lyrics_file, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"  ✓ 歌词已保存: {lyrics_file}")
        project_info['lyrics_file'] = str(lyrics_file)

        # 步骤3: 生成新的专辑封面（基于分析结果）
        print_step(3, "生成专辑封面")
        cover_result = doubao_image.generate_album_cover(
            title="AI音乐作品",
            style=music_elements['style'],
            mood=music_elements['emotion'],
            color_scheme=music_elements['color_tone'],
            elements=music_elements.get('keywords', ''),
            size="1K"
        )
        print(f"✓ 封面生成成功")
        print(f"  URL: {cover_result['url']}")

        # 下载封面
        cover_file = doubao_downloader.download_image(
            url=cover_result['url'],
            save_dir=project_dir,
            filename="cover.jpg"
        )
        print(f"  ✓ 封面已保存: {cover_file}")
        project_info['cover_file'] = cover_file
        project_info['cover_url'] = cover_result['url']

        # 步骤4: 提交MV生成任务
        print_step(4, "提交MV生成任务")
        mv_result = doubao_video.generate_mv(
            lyrics=lyrics,
            style=music_elements['style'],
            mood=music_elements['emotion'],
            cover_image_url=cover_result['url'],
            ratio="16:9",
            duration=5
        )
        print(f"✓ MV任务提交成功")
        print(f"  任务ID: {mv_result['task_id']}")
        print(f"  提示词: {mv_result['prompt'][:100]}...")
        project_info['mv_task_id'] = mv_result['task_id']

        # 保存项目信息
        save_project_info(project_dir, project_info)

        # 总结
        print_header("场景2 完成！")
        print(f"✓ 歌词: {lyrics_file}")
        print(f"✓ 封面: {cover_file}")
        print(f"✓ MV任务ID: {mv_result['task_id']}")
        print(f"✓ 项目文件夹: {project_dir}")
        print(f"\n💡 提示: 访问豆包控制台查看MV生成进度")
        print(f"   https://console.volcengine.com/")

        return project_info

    except Exception as e:
        print(f"\n✗ 创作失败: {e}")
        return None


# ============================================================
# 场景3: 完整制作流程（创意 → 策划 → 创作 → 优化）
# ============================================================

def scenario_3_complete_production():
    """场景3: 完整音乐制作流程"""
    print_header("场景3: 完整音乐制作流程")

    # 创建项目文件夹
    project_dir = create_project_folder()
    print(f"📁 项目文件夹: {project_dir}\n")

    # 定义创作方向
    concept = {
        "title": "时光旅行者",
        "theme": "时间与记忆",
        "style": "电子流行",
        "mood": "梦幻科技感",
        "target_audience": "年轻人",
        "key_message": "珍惜当下"
    }

    print("🎵 创作概念:")
    for key, value in concept.items():
        print(f"  {key}: {value}")

    project_info = {
        "concept": concept,
        "created_at": datetime.now().isoformat(),
        "workflow": []
    }

    try:
        # 阶段1: 创作初稿歌词
        print_step(1, "创作初稿歌词")
        initial_lyrics = doubao_text.generate_lyrics(
            prompt=f"{concept['theme']}，传达{concept['key_message']}的主题",
            style=concept['style'],
            mood=concept['mood'],
            temperature=0.9  # 高温度，更有创造性
        )
        print(f"✓ 初稿完成 ({len(initial_lyrics)}字)")
        project_info['workflow'].append("初稿歌词创作")

        # 阶段2: 优化歌词
        print_step(2, "优化歌词")
        refined_lyrics = doubao_text.refine_lyrics(
            original_lyrics=initial_lyrics,
            refinement_request=f"增强{concept['mood']}的氛围感，让副歌更有感染力",
            temperature=0.5  # 低温度，保持原意
        )
        print(f"✓ 歌词优化完成")
        print(f"\n优化后的歌词预览:\n{refined_lyrics[:300]}...\n")
        project_info['workflow'].append("歌词优化")

        # 保存歌词版本
        lyrics_dir = Path(project_dir) / "lyrics_versions"
        lyrics_dir.mkdir(exist_ok=True)

        with open(lyrics_dir / "v1_initial.txt", 'w', encoding='utf-8') as f:
            f.write(initial_lyrics)
        with open(lyrics_dir / "v2_refined.txt", 'w', encoding='utf-8') as f:
            f.write(refined_lyrics)

        final_lyrics_file = Path(project_dir) / "lyrics_final.txt"
        with open(final_lyrics_file, 'w', encoding='utf-8') as f:
            f.write(refined_lyrics)

        print(f"  ✓ 歌词版本已保存:")
        print(f"    - 初稿: {lyrics_dir / 'v1_initial.txt'}")
        print(f"    - 优化: {lyrics_dir / 'v2_refined.txt'}")
        print(f"    - 最终: {final_lyrics_file}")

        project_info['lyrics_file'] = str(final_lyrics_file)

        # 阶段3: 设计封面（多个方案）
        print_step(3, "设计多个封面方案")
        cover_configs = [
            {"theme": "科技感", "elements": "未来城市、霓虹灯、科技元素"},
            {"theme": "梦幻感", "elements": "星空、时钟、梦境"},
            {"theme": "复古感", "elements": "旧照片、怀旧色调、时光"}
        ]

        cover_urls = []
        for idx, config in enumerate(cover_configs, 1):
            print(f"\n  方案{idx}: {config['theme']}")
            result = doubao_image.generate_album_cover(
                title=concept['title'],
                style=concept['style'],
                mood=f"{concept['mood']} - {config['theme']}",
                elements=config['elements'],
                size="1K"
            )
            cover_urls.append(result['url'])
            print(f"    ✓ URL: {result['url']}")

        project_info['workflow'].append("多方案封面设计")

        # 阶段4: 下载所有封面
        print_step(4, "下载所有封面方案")
        cover_files = doubao_downloader.batch_download_images(
            urls=cover_urls,
            save_dir=str(Path(project_dir) / "covers"),
            prefix="cover_option"
        )
        print(f"✓ 所有封面已下载")
        project_info['cover_files'] = [f for f in cover_files if f]
        project_info['workflow'].append("封面下载")

        # 阶段5: 生成概念视频
        print_step(5, "生成概念MV")
        mv_result = doubao_video.generate_concept_video(
            concept=f"{concept['theme']} - {concept['key_message']}",
            style=concept['style'],
            color_tone="未来科技感，蓝紫色调",
            camera_movement="镜头缓缓推进和旋转",
            ratio="16:9",
            duration=5
        )
        print(f"✓ MV任务提交成功")
        print(f"  任务ID: {mv_result['task_id']}")
        project_info['mv_task_id'] = mv_result['task_id']
        project_info['workflow'].append("MV生成")

        # 保存项目信息
        save_project_info(project_dir, project_info)

        # 总结
        print_header("场景3 完成！完整制作流程")
        print(f"\n工作流程:")
        for idx, step in enumerate(project_info['workflow'], 1):
            print(f"  {idx}. {step}")

        print(f"\n生成的资源:")
        print(f"  ✓ 歌词版本: 初稿、优化版、最终版")
        print(f"  ✓ 封面方案: {len(cover_files)} 个")
        print(f"  ✓ MV任务ID: {mv_result['task_id']}")
        print(f"  ✓ 项目文件夹: {project_dir}")

        return project_info

    except Exception as e:
        print(f"\n✗ 制作失败: {e}")
        return None


# ============================================================
# 场景4: 批量创作
# ============================================================

def scenario_4_batch_creation():
    """场景4: 批量创作多首歌曲"""
    print_header("场景4: 批量创作 - 一次创作多首歌")

    # 定义创作列表
    songs = [
        {"title": "春之声", "theme": "春天的生机", "style": "轻快流行", "mood": "欢快"},
        {"title": "夏日海", "theme": "夏天的海边", "style": "清新民谣", "mood": "放松"},
        {"title": "秋叶舞", "theme": "秋天的落叶", "style": "抒情钢琴", "mood": "怀旧"},
        {"title": "冬雪夜", "theme": "冬天的雪夜", "style": "古典", "mood": "宁静"}
    ]

    print(f"📝 计划创作 {len(songs)} 首歌曲:\n")
    for idx, song in enumerate(songs, 1):
        print(f"  {idx}. 《{song['title']}》 - {song['style']}")

    # 创建批量项目文件夹
    batch_dir = create_project_folder("outputs/batch_projects")
    print(f"\n📁 批量项目文件夹: {batch_dir}\n")

    results = []

    try:
        for idx, song in enumerate(songs, 1):
            print(f"\n{'='*70}")
            print(f"  正在创作第 {idx}/{len(songs)} 首: 《{song['title']}》")
            print(f"{'='*70}")

            # 为每首歌创建子文件夹
            song_dir = Path(batch_dir) / f"{idx:02d}_{song['title']}"
            song_dir.mkdir(exist_ok=True)

            try:
                # 生成歌词
                print(f"\n  步骤1: 生成歌词...")
                lyrics = doubao_text.generate_lyrics(
                    prompt=song['theme'],
                    style=song['style'],
                    mood=song['mood'],
                    temperature=0.8
                )
                print(f"    ✓ 歌词完成 ({len(lyrics)}字)")

                # 保存歌词
                lyrics_file = song_dir / "lyrics.txt"
                with open(lyrics_file, 'w', encoding='utf-8') as f:
                    f.write(lyrics)

                # 生成封面
                print(f"  步骤2: 生成封面...")
                cover_result = doubao_image.generate_album_cover(
                    title=song['title'],
                    style=song['style'],
                    mood=song['mood'],
                    size="1K"
                )
                print(f"    ✓ 封面完成")

                # 下载封面
                print(f"  步骤3: 下载封面...")
                cover_file = doubao_downloader.download_image(
                    url=cover_result['url'],
                    save_dir=str(song_dir),
                    filename="cover.jpg"
                )
                print(f"    ✓ 已保存")

                # 记录结果
                result = {
                    "title": song['title'],
                    "status": "success",
                    "lyrics_file": str(lyrics_file),
                    "cover_file": cover_file,
                    "folder": str(song_dir)
                }
                results.append(result)

                print(f"\n  ✓ 《{song['title']}》创作完成！")

            except Exception as e:
                print(f"\n  ✗ 《{song['title']}》创作失败: {e}")
                results.append({
                    "title": song['title'],
                    "status": "failed",
                    "error": str(e)
                })

        # 保存批量项目信息
        batch_info = {
            "total": len(songs),
            "success": sum(1 for r in results if r['status'] == 'success'),
            "failed": sum(1 for r in results if r['status'] == 'failed'),
            "results": results,
            "created_at": datetime.now().isoformat()
        }

        info_file = Path(batch_dir) / "batch_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(batch_info, f, ensure_ascii=False, indent=2)

        # 总结
        print_header("场景4 批量创作完成！")
        print(f"总计: {batch_info['total']} 首")
        print(f"成功: {batch_info['success']} 首 ✓")
        print(f"失败: {batch_info['failed']} 首 ✗")
        print(f"\n批量项目文件夹: {batch_dir}")

        # 列出成功的作品
        if batch_info['success'] > 0:
            print(f"\n成功创作的歌曲:")
            for r in results:
                if r['status'] == 'success':
                    print(f"  ✓ 《{r['title']}》")
                    print(f"    文件夹: {r['folder']}")

        return batch_info

    except Exception as e:
        print(f"\n✗ 批量创作失败: {e}")
        return None


# ============================================================
# 场景5: 交互式创作助手
# ============================================================

def scenario_5_interactive_creator():
    """场景5: 交互式创作助手"""
    print_header("场景5: 交互式音乐创作助手")

    print("""
欢迎使用AI音乐创作助手！

我可以帮你：
1. 根据主题创作歌词
2. 生成专辑封面
3. 分析图片并创作音乐
4. 生成音乐MV

让我们开始创作吧！
    """)

    # 创建项目文件夹
    project_dir = create_project_folder()
    print(f"📁 项目文件夹: {project_dir}\n")

    project_info = {
        "created_at": datetime.now().isoformat(),
        "interactions": []
    }

    try:
        # 获取用户输入
        print("请告诉我你的创作想法：\n")

        title = input("歌曲名称: ").strip() or "未命名歌曲"
        theme = input("主题/内容 (如: 爱情、友情、梦想): ").strip() or "生活感悟"
        style = input("音乐风格 (如: 流行、摇滚、民谣): ").strip() or "流行"
        mood = input("情绪氛围 (如: 欢快、忧郁、激情): ").strip() or "轻快"

        project_info['title'] = title
        project_info['theme'] = theme
        project_info['style'] = style
        project_info['mood'] = mood

        print(f"\n很好！我将为你创作《{title}》")
        print(f"主题: {theme}, 风格: {style}, 氛围: {mood}")

        input("\n按回车键开始创作...")

        # 步骤1: 生成歌词
        print_step(1, "创作歌词")
        lyrics = doubao_text.generate_lyrics(
            prompt=f"{theme}",
            style=style,
            mood=mood,
            temperature=0.8
        )
        print(f"✓ 歌词创作完成！\n")
        print("="*70)
        print(lyrics)
        print("="*70)

        # 询问是否满意
        satisfied = input("\n你对歌词满意吗？(y/n，直接回车表示满意): ").strip().lower()

        if satisfied == 'n':
            refinement = input("请告诉我需要如何修改: ").strip()
            if refinement:
                print(f"\n正在优化歌词...")
                lyrics = doubao_text.refine_lyrics(
                    original_lyrics=lyrics,
                    refinement_request=refinement,
                    temperature=0.6
                )
                print(f"✓ 歌词优化完成！\n")
                print("="*70)
                print(lyrics)
                print("="*70)
                project_info['interactions'].append(f"歌词优化: {refinement}")

        # 保存歌词
        lyrics_file = Path(project_dir) / "lyrics.txt"
        with open(lyrics_file, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"\n✓ 歌词已保存: {lyrics_file}")
        project_info['lyrics_file'] = str(lyrics_file)

        # 步骤2: 生成封面
        print_step(2, "设计专辑封面")

        cover_elements = input("封面需要包含哪些元素？(如: 海边、夕阳、吉他): ").strip()
        if not cover_elements:
            cover_elements = theme

        print(f"\n正在生成封面...")
        cover_result = doubao_image.generate_album_cover(
            title=title,
            style=style,
            mood=mood,
            elements=cover_elements,
            size="1K"
        )

        print(f"✓ 封面设计完成！")
        print(f"  预览URL: {cover_result['url']}")

        # 下载封面
        cover_file = doubao_downloader.download_image(
            url=cover_result['url'],
            save_dir=project_dir,
            filename="cover.jpg"
        )
        print(f"  ✓ 已保存: {cover_file}")
        project_info['cover_file'] = cover_file

        # 步骤3: 询问是否生成MV
        print_step(3, "音乐MV")
        create_mv = input("是否生成音乐MV？(y/n): ").strip().lower()

        if create_mv == 'y':
            print(f"\n正在提交MV生成任务...")
            mv_result = doubao_video.generate_mv(
                lyrics=lyrics,
                style=style,
                mood=mood,
                cover_image_url=cover_result['url'],
                ratio="16:9"
            )

            print(f"✓ MV任务提交成功！")
            print(f"  任务ID: {mv_result['task_id']}")
            print(f"  请访问豆包控制台查看进度: https://console.volcengine.com/")
            project_info['mv_task_id'] = mv_result['task_id']

        # 保存项目信息
        save_project_info(project_dir, project_info)

        # 完成总结
        print_header("创作完成！")
        print(f"歌曲: 《{title}》")
        print(f"风格: {style}")
        print(f"\n生成的文件:")
        print(f"  📝 歌词: {lyrics_file}")
        print(f"  🎨 封面: {cover_file}")
        if 'mv_task_id' in project_info:
            print(f"  🎬 MV任务: {project_info['mv_task_id']}")
        print(f"\n📁 项目文件夹: {project_dir}")
        print(f"\n感谢使用AI音乐创作助手！")

        return project_info

    except KeyboardInterrupt:
        print("\n\n创作已取消。")
        return None
    except Exception as e:
        print(f"\n✗ 创作失败: {e}")
        return None


# ============================================================
# 主菜单
# ============================================================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  🎵 豆包AI音乐创作完整示例")
    print("="*70)

    print("""
请选择创作场景：

1. 快速创作 - 输入主题，快速生成歌词+封面
2. 图片成歌 - 从图片到完整音乐作品（歌词+封面+MV）
3. 完整制作 - 专业级音乐制作流程（多版本迭代）
4. 批量创作 - 一次创作多首歌曲
5. 交互式创作 - 与AI助手互动创作

0. 退出
    """)

    try:
        choice = input("请选择 (0-5): ").strip()

        if choice == "1":
            scenario_1_quick_creation()
        elif choice == "2":
            scenario_2_image_to_song()
        elif choice == "3":
            scenario_3_complete_production()
        elif choice == "4":
            scenario_4_batch_creation()
        elif choice == "5":
            scenario_5_interactive_creator()
        elif choice == "0":
            print("\n再见！")
            return
        else:
            print("\n无效的选项！")
            return

        # 询问是否继续
        print("\n" + "="*70)
        continue_choice = input("\n是否继续尝试其他场景？(y/n): ").strip().lower()
        if continue_choice == 'y':
            main()
        else:
            print("\n感谢使用！再见！")

    except KeyboardInterrupt:
        print("\n\n程序已退出。")
    except Exception as e:
        print(f"\n程序出错: {e}")


if __name__ == "__main__":
    main()
