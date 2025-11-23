"""
联合测试：先通过 Suno 上传图片获取 URL，再调用豆包视觉理解接口。
运行命令示例：
    .\.venv\Scripts\python tests\test_upload_and_vision.py
"""
import json
import sys
from pathlib import Path

# 确保项目根目录在 sys.path，便于模块导入
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.clients.suno import SunoClient
from modules.clients.doubao import DoubaoClient


def main():
    img_path = ROOT / 'imag.png'
    if not img_path.exists():
        print('本地缺少 imag.png，终止测试', file=sys.stderr)
        sys.exit(1)

    print('[1] 上传图片到 Suno...')
    client = SunoClient()
    upload_url = None
    try:
        upload_url = client.upload_stream(str(img_path), upload_path='images')
        print(f'上传成功 URL: {upload_url}')
    except Exception as e:
        print(f'上传失败: {e}', file=sys.stderr)
        sys.exit(1)

    print('\n[2] 调用豆包视觉理解...')
    doubao = DoubaoClient()
    try:
        description = doubao.understand_image(
            image_url=upload_url,
            question='描述画面主体、场景与情绪，并给出一句中文标题。'
        )
        print('豆包返回:')
        print(description)
    except Exception as e:
        print(f'豆包图像理解失败: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
