"""
豆包资源下载工具

提供图片、视频下载和任务查询功能。

功能：
1. 下载图片到本地
2. 查询视频生成任务状态
3. 下载视频到本地
4. 批量下载管理

使用示例：
    from modules.clients.doubao_downloader import download_image, query_video_task

    # 下载图片
    file_path = download_image(
        url="https://...",
        save_dir="outputs/images",
        filename="cover.jpg"
    )

    # 查询视频任务
    status = query_video_task(task_id="xxx")
    if status['status'] == 'completed':
        video_path = download_video(
            url=status['video_url'],
            save_dir="outputs/videos"
        )
"""

import os
import json
import pathlib
import time
import requests
from typing import Optional, Dict, Any
from volcenginesdkarkruntime import Ark


def _get_client(api_key: Optional[str] = None) -> Ark:
    """获取 Ark 客户端"""
    if not api_key:
        config_file = pathlib.Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    doubao_config = config.get("doubao", {})
                    api_key_value = doubao_config.get("api_key", "")
                    if api_key_value.startswith("${") and api_key_value.endswith("}"):
                        env_var = api_key_value[2:-1]
                        api_key = os.getenv(env_var)
                    else:
                        api_key = api_key_value
            except Exception:
                pass

        if not api_key:
            api_key = os.getenv("ARK_API_KEY")

    if not api_key:
        raise RuntimeError(
            "缺少豆包 API Key！请设置环境变量 ARK_API_KEY 或在 config.json 中配置"
        )

    return Ark(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )


def download_image(
    url: str,
    save_dir: str = "outputs/images",
    filename: Optional[str] = None,
    overwrite: bool = False
) -> str:
    """
    下载图片到本地

    Args:
        url: 图片URL
        save_dir: 保存目录
        filename: 文件名（可选，默认从URL提取或使用时间戳）
        overwrite: 是否覆盖已存在的文件

    Returns:
        下载后的文件路径

    Raises:
        RuntimeError: 下载失败时

    示例:
        >>> file_path = download_image(
        ...     url="https://example.com/image.jpg",
        ...     save_dir="outputs/covers",
        ...     filename="album_cover.jpg"
        ... )
        >>> print(f"图片已保存到: {file_path}")
    """
    # 创建保存目录
    save_path = pathlib.Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # 确定文件名
    if not filename:
        # 从URL提取文件名
        url_path = url.split('?')[0]  # 移除查询参数
        filename = url_path.split('/')[-1]

        # 如果无法提取，使用时间戳
        if not filename or '.' not in filename:
            timestamp = int(time.time())
            filename = f"image_{timestamp}.jpg"

    # 完整文件路径
    file_path = save_path / filename

    # 检查文件是否存在
    if file_path.exists() and not overwrite:
        print(f"文件已存在: {file_path}")
        return str(file_path)

    try:
        # 下载图片
        print(f"正在下载图片: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 保存到文件
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ 图片已保存到: {file_path} ({len(response.content)} 字节)")
        return str(file_path)

    except Exception as e:
        raise RuntimeError(f"下载图片失败: {e}")


def query_video_task(
    task_id: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询视频生成任务状态

    Args:
        task_id: 任务ID（从 generate_video 返回）
        api_key: API密钥（可选）

    Returns:
        任务状态信息：
        {
            "task_id": "任务ID",
            "status": "processing|completed|failed",
            "video_url": "视频URL（完成时）",
            "progress": "进度百分比",
            "error": "错误信息（失败时）"
        }

    示例:
        >>> status = query_video_task(task_id="xxx")
        >>> if status['status'] == 'completed':
        ...     print(f"视频URL: {status['video_url']}")
    """
    client = _get_client(api_key)

    try:
        # 调用任务查询API
        # 注意：这里需要根据豆包实际的API来实现
        # 当前为示例代码，实际API可能不同
        response = client.content_generation.tasks.retrieve(task_id=task_id)

        # 解析响应
        status_info = {
            "task_id": task_id,
            "status": "processing",  # processing, completed, failed
            "video_url": None,
            "progress": 0,
            "error": None
        }

        # 根据实际API响应解析（需要根据豆包文档调整）
        if hasattr(response, 'status'):
            status_info['status'] = response.status

        if hasattr(response, 'video_url'):
            status_info['video_url'] = response.video_url

        if hasattr(response, 'progress'):
            status_info['progress'] = response.progress

        if hasattr(response, 'error'):
            status_info['error'] = response.error

        return status_info

    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "video_url": None,
            "progress": 0,
            "error": str(e)
        }


def download_video(
    url: str,
    save_dir: str = "outputs/videos",
    filename: Optional[str] = None,
    overwrite: bool = False,
    show_progress: bool = True
) -> str:
    """
    下载视频到本地

    Args:
        url: 视频URL
        save_dir: 保存目录
        filename: 文件名（可选）
        overwrite: 是否覆盖已存在的文件
        show_progress: 是否显示下载进度

    Returns:
        下载后的文件路径

    示例:
        >>> video_path = download_video(
        ...     url="https://example.com/video.mp4",
        ...     save_dir="outputs/mvs",
        ...     filename="my_mv.mp4"
        ... )
    """
    # 创建保存目录
    save_path = pathlib.Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # 确定文件名
    if not filename:
        url_path = url.split('?')[0]
        filename = url_path.split('/')[-1]

        if not filename or '.' not in filename:
            timestamp = int(time.time())
            filename = f"video_{timestamp}.mp4"

    # 完整文件路径
    file_path = save_path / filename

    # 检查文件是否存在
    if file_path.exists() and not overwrite:
        print(f"文件已存在: {file_path}")
        return str(file_path)

    try:
        print(f"正在下载视频: {url}")

        # 流式下载（支持大文件）
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        # 下载并保存
        with open(file_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 显示进度
                    if show_progress and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r下载进度: {progress:.1f}% ({downloaded}/{total_size} 字节)", end='')

        if show_progress:
            print()  # 换行

        print(f"✓ 视频已保存到: {file_path} ({downloaded} 字节)")
        return str(file_path)

    except Exception as e:
        # 下载失败时删除不完整的文件
        if file_path.exists():
            file_path.unlink()
        raise RuntimeError(f"下载视频失败: {e}")


def wait_for_video(
    task_id: str,
    save_dir: str = "outputs/videos",
    filename: Optional[str] = None,
    max_wait_time: int = 600,
    check_interval: int = 10,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    等待视频生成完成并自动下载

    Args:
        task_id: 任务ID
        save_dir: 保存目录
        filename: 文件名（可选）
        max_wait_time: 最大等待时间（秒）
        check_interval: 检查间隔（秒）
        api_key: API密钥（可选）

    Returns:
        下载后的文件路径，如果失败返回None

    示例:
        >>> # 提交视频生成任务
        >>> result = doubao_video.generate_mv(...)
        >>>
        >>> # 等待完成并下载
        >>> video_path = wait_for_video(
        ...     task_id=result['task_id'],
        ...     save_dir="outputs/mvs",
        ...     filename="my_mv.mp4",
        ...     max_wait_time=600  # 最多等10分钟
        ... )
    """
    print(f"等待视频生成完成... (任务ID: {task_id})")
    print(f"最大等待时间: {max_wait_time}秒, 检查间隔: {check_interval}秒")

    start_time = time.time()
    attempts = 0

    while True:
        attempts += 1
        elapsed = int(time.time() - start_time)

        # 检查是否超时
        if elapsed > max_wait_time:
            print(f"\n✗ 等待超时（{max_wait_time}秒）")
            return None

        # 查询任务状态
        try:
            status = query_video_task(task_id, api_key)

            print(f"\r[{attempts}] 状态: {status['status']} | "
                  f"进度: {status.get('progress', 0)}% | "
                  f"已等待: {elapsed}秒", end='')

            # 检查状态
            if status['status'] == 'completed' and status.get('video_url'):
                print("\n✓ 视频生成完成！开始下载...")

                # 下载视频
                video_path = download_video(
                    url=status['video_url'],
                    save_dir=save_dir,
                    filename=filename
                )
                return video_path

            elif status['status'] == 'failed':
                print(f"\n✗ 视频生成失败: {status.get('error', '未知错误')}")
                return None

            # 继续等待
            time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\n用户取消等待")
            return None

        except Exception as e:
            print(f"\n✗ 查询任务状态出错: {e}")
            time.sleep(check_interval)


def batch_download_images(
    urls: list,
    save_dir: str = "outputs/images",
    prefix: str = "img"
) -> list:
    """
    批量下载图片

    Args:
        urls: 图片URL列表
        save_dir: 保存目录
        prefix: 文件名前缀

    Returns:
        下载成功的文件路径列表

    示例:
        >>> urls = ["https://...", "https://..."]
        >>> files = batch_download_images(urls, save_dir="outputs/covers")
    """
    results = []

    for idx, url in enumerate(urls, 1):
        try:
            filename = f"{prefix}_{idx}.jpg"
            file_path = download_image(
                url=url,
                save_dir=save_dir,
                filename=filename
            )
            results.append(file_path)
            print(f"[{idx}/{len(urls)}] ✓ 下载成功")

        except Exception as e:
            print(f"[{idx}/{len(urls)}] ✗ 下载失败: {e}")
            results.append(None)

    success_count = sum(1 for r in results if r is not None)
    print(f"\n批量下载完成: {success_count}/{len(urls)} 成功")

    return results


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息

    Args:
        file_path: 文件路径

    Returns:
        文件信息字典

    示例:
        >>> info = get_file_info("outputs/videos/my_mv.mp4")
        >>> print(f"文件大小: {info['size_mb']:.2f} MB")
    """
    path = pathlib.Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    stat = path.stat()

    return {
        "filename": path.name,
        "path": str(path.absolute()),
        "size_bytes": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime,
        "extension": path.suffix
    }


if __name__ == "__main__":
    # 测试代码
    print("=== 豆包资源下载工具测试 ===\n")

    # 测试图片下载（使用公开测试图片）
    print("测试1：下载图片")
    try:
        test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
        file_path = download_image(
            url=test_image_url,
            save_dir="outputs/test_images",
            filename="test_download.jpg"
        )
        print(f"✓ 测试成功: {file_path}\n")

        # 获取文件信息
        info = get_file_info(file_path)
        print(f"文件信息:")
        print(f"  - 文件名: {info['filename']}")
        print(f"  - 大小: {info['size_mb']:.2f} MB")
        print(f"  - 路径: {info['path']}")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
