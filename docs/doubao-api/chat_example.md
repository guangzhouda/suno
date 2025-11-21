#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用豆包(Doubao) API 清洗和优化爬取的Markdown内容（支持目录批处理）

功能:
1. 逐个读取 Markdown 文件(Q&A格式)，避免一次性合并导致上下文过大
2. 使用豆包API对每个文件内的Q&A逐条清洗与优化
3. 输出到独立的 cleaned 文件，互不合并

用法:
    # 设置环境变量
    export ARK_API_KEY="your_api_key"  # Linux/Mac
    set ARK_API_KEY=your_api_key       # Windows

    # 目录批处理（默认扫描 output/md_extracted）
    python clean_with_doubao.py
    python clean_with_doubao.py --input-dir ../output/md_extracted --output-dir ../output/cleaned_md_extracted
    
    # 单文件（维持兼容）
    python clean_with_doubao.py --input output/result.md
    python clean_with_doubao.py --input ../output/result.md --output ../output/result_cleaned.md
    
    # 其他
    python clean_with_doubao.py --model deepseek-v3-250324 --delay 0.8 --limit 10
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional

from volcenginesdkarkruntime import Ark


def parse_qa_from_markdown(md_path: str) -> List[Tuple[str, str]]:
    """
    解析Markdown中的Q&A对

    格式:
    # 问题标题
    
    答案内容
    
    ---（分隔符）
    
    Returns:
        [(question, answer), ...]
    """
    content = Path(md_path).read_text(encoding='utf-8')
    blocks = re.split(r'\n---+\n', content)
    qa_pairs: List[Tuple[str, str]] = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
    
        match = re.match(r'^#\s+(.+?)(?:\n|$)', block, re.MULTILINE)
        if not match:
            continue
    
        question = match.group(1).strip()
        answer = block[match.end():].strip()
    
        if question and answer:
            qa_pairs.append((question, answer))
    
    return qa_pairs


def clean_content_with_ai(
    client: Ark,
    content: str,
    model: str = "deepseek-v3-250324"
) -> str:
    """
    使用AI清洗和结构化内容
    """
    prompt = f"""你是一个专业的知识库内容编辑助手。请对以下文本内容进行清洗和结构化整理。
输入可能是 FAQ、问答、教程、公告或说明等，不一定包含"问题 / 答案"的结构。
目标：
1. 尽量整理为清晰的问答形式（Q&A）；
2. 若原文中无明确问题，则根据语义提炼出合适的问题标题，并以问答形式组织内容；
3. 若完全无法归纳为问答，则整理为条理清晰的说明性文档。
要求：
1. 保留所有关键信息和步骤；
2. 去除冗余、重复、废话或营销性语句；
3. 优化语言，使表达更简洁清晰；
4. 使用 Markdown 格式（标题、列表、代码块等）；
5. 保留所有图片或链接；
6. 不添加原文中没有的信息；
7. 输出时以问答结构为优先；
8. 仅输出结果内容，不加任何说明文字。

输入内容：
{content}

输出格式示例：
### 问题
如何查看产品是否为正品？

### 答案
- 扫描包装上的二维码验证真伪；
- 防伪码通常位于包装顶部或底部；
- 国内扫码会显示生产日期、防伪码和序列号；
- 海外扫码会展示相应验证信息。

若无法整理为问答，可改为：
### 使用说明
这里填写优化后的段落内容。
"""

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        cleaned = completion.choices[0].message.content.strip()
        return cleaned if cleaned else content
    except Exception as e:
        print(f"  [!] API调用失败: {e}")
        return content  # 失败时返回原始内容


def process_single_file(
    client: Ark,
    md_path: Path,
    out_path: Path,
    model: str,
    delay: float,
    limit: int
) -> bool:
    """
    处理单个 .md 文件：解析 -> 逐条清洗 -> 保存
    """
    print(f"\n===== 处理文件: {md_path} =====")
    try:
        qa_pairs = parse_qa_from_markdown(str(md_path))
    except Exception as e:
        print(f"[!] 解析失败: {e}")
        return False

    print(f"[+] 解析到 {len(qa_pairs)} 个Q&A对")
    if not qa_pairs:
        print("[!] 跳过：未找到任何Q&A内容")
        return False
    
    if limit > 0:
        qa_pairs = qa_pairs[:limit]
        print(f"[*] 本文件限制处理前 {limit} 个Q&A")
    
    cleaned_blocks: List[str] = []
    success, unchanged = 0, 0
    
    for i, (q, a) in enumerate(qa_pairs, 1):
        print(f"[{i}/{len(qa_pairs)}] {q}")
        full = f"# {q}\n\n{a}"
        cleaned = clean_content_with_ai(client, full, model)
        if cleaned != full:
            print(f"  [+] 清洗成功 (原{len(full)}字 → {len(cleaned)}字)")
            success += 1
        else:
            print("  [=] 保持原样")
            unchanged += 1
    
        cleaned_blocks.append(cleaned if cleaned.endswith("\n") else cleaned + "\n")
    
        if i < len(qa_pairs):
            time.sleep(delay)
    
    # 保存本文件的清洗结果（逐个文件独立输出）
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for block in cleaned_blocks:
                f.write(block)
                if not block.rstrip().endswith('---'):
                    f.write("\n---\n\n")
                else:
                    f.write("\n")
        print(f"[✔] 已保存: {out_path}  | 成功清洗 {success}, 未变更 {unchanged}")
        return True
    except Exception as e:
        print(f"[!] 保存失败: {e}")
        return False


def discover_md_files(input_dir: Path) -> List[Path]:
    files = sorted([p for p in input_dir.glob("*.md") if p.is_file()])
    print(f"[i] 在目录中找到 {len(files)} 个 .md 文件: {input_dir}")
    return files


def main():
    parser = argparse.ArgumentParser(
        description='使用豆包API清洗Markdown知识库（支持目录批处理）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量:
  ARK_API_KEY    豆包API密钥(必需)

示例:
  # 目录批处理（默认扫描 output/md_extracted）
  python clean_with_doubao.py
  python clean_with_doubao.py --input-dir output/md_extracted --output-dir output/cleaned_md_extracted

  # 单文件
  python clean_with_doubao.py --input output/result.md
  python clean_with_doubao.py --input output/result.md --output output/result_cleaned.md

  # 自定义模型和延迟
  python clean_with_doubao.py --model deepseek-v3-250324 --delay 1.0

  # 限制每文件处理前10个Q&A(测试用)
  python clean_with_doubao.py --limit 10
        """
    )

    # 输入互斥：input 或 input-dir
    parser.add_argument('--input', help='输入Markdown文件（单文件模式）')
    parser.add_argument('--input-dir', default='output/md_extracted', help='输入目录(批处理模式)')
    parser.add_argument('--output', help='输出Markdown文件（单文件模式），未指定则自动 *_cleaned.md')
    parser.add_argument('--output-dir', default='output/cleaned_md_extracted', help='输出目录(批处理模式)')
    parser.add_argument('--model', default='deepseek-v3-250324', help='模型ID')
    parser.add_argument('--delay', type=float, default=0.5, help='API调用间隔(秒)')
    parser.add_argument('--limit', type=int, default=0, help='每文件限制处理数量(0=全部)')
    parser.add_argument('--base-url', default='https://ark.cn-beijing.volces.com/api/v3', help='API Base URL')
    
    args = parser.parse_args()
    
    # 检查环境变量
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("[!] 错误: 未设置 ARK_API_KEY 环境变量")
        print("请运行: export ARK_API_KEY='your_api_key'  (Linux/Mac)")
        print("或运行: set ARK_API_KEY=your_api_key       (Windows)")
        return 1
    
    # 初始化API客户端（只初始化一次）
    try:
        client = Ark(api_key=api_key, base_url=args.base_url)
        print("[+] API客户端初始化成功")
    except Exception as e:
        print(f"[!] 初始化失败: {e}")
        return 1
    
    # 模式判断：优先目录批处理（若提供 --input 则走单文件）
    if args.input:
        # 单文件模式
        in_path = Path(args.input)
        if not in_path.exists():
            print(f"[!] 输入文件不存在: {in_path}")
            return 1
    
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = in_path.parent / f"{in_path.stem}_cleaned{in_path.suffix}"
    
        ok = process_single_file(
            client=client,
            md_path=in_path,
            out_path=out_path,
            model=args.model,
            delay=args.delay,
            limit=args.limit
        )
        return 0 if ok else 1
    
    # 目录批处理模式
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"[!] 输入目录不存在: {input_dir}")
        return 1
    
    files = discover_md_files(input_dir)
    if not files:
        print("[!] 目录中没有找到 .md 文件")
        return 1
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total, ok_cnt, fail_cnt = 0, 0, 0
    for md_file in files:
        total += 1
        out_file = output_dir / f"{md_file.stem}_cleaned.md"
        ok = process_single_file(
            client=client,
            md_path=md_file,
            out_path=out_file,
            model=args.model,
            delay=args.delay,
            limit=args.limit
        )
        if ok:
            ok_cnt += 1
        else:
            fail_cnt += 1
    
    print("\n================ 总结 ================")
    print(f"处理文件总数: {total}")
    print(f"成功: {ok_cnt}")
    print(f"失败: {fail_cnt}")
    print("=====================================")
    return 0 if fail_cnt == 0 else 2


if __name__ == '__main__':
    sys.exit(main())