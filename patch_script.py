from pathlib import Path
text = Path("maono.html").read_text(encoding="utf-8").replace("\r\n", "\n")
old_lines = [
    "// \u5c1d\u8bd5\u5148\u751f\u6210\u6b4c\u8bcd\uff08\u9664 extend/cover \u5916\uff09",
    "  let lyricsText = input;",
    "  let titleText = 'AI Song';",
    "  if (mode !== 'extend' && mode !== 'cover') {",
    "    let promptForLyrics = input;",
    "    if (mode === 'image_to_song' && media) {",
    "      const desc = await understandImage(media);",
    "      promptForLyrics = `${desc}\\n\\n\u989d\u5916\u8981\u6c42\uff1a${input}`;",
    "    }",
    "    const lyr = await fetchLyrics(promptForLyrics);",
    "    lyricsText = lyr.text || input;",
    "    titleText = lyr.title || 'AI Song';",
    "    document.getElementById('lyrics').textContent = lyricsText;",
    "  }",
    "  lastLyricsText = lyricsText;",
    "  lastTitleText = titleText;",
]
new_lines = [
    "// \u5c1d\u8bd5\u5148\u751f\u6210\u6b4c\u8bcd\uff08\u9664 extend/cover \u5916\uff09",
    "  let lyricsText = input;",
    "  let titleText = 'AI Song';",
    "  if (mode !== 'extend' && mode !== 'cover') {",
    "    let promptForLyrics = input;",
    "    let lyricsGenerated = false;",
    "    if (mode === 'image_to_song' && media) {",
    "      // \u4f18\u5148\u56fe\u7247\u76f4\u51fa\u6b4c\u8bcd\uff0c\u5931\u8d25\u518d\u7528\u63cf\u8ff0+\u6587\u672c\u751f\u6210",
    "      const imgLyrics = await imageToLyrics(media, input);",
    "      if (imgLyrics && imgLyrics.text) {",
    "        lyricsText = imgLyrics.text;",
    "        titleText = imgLyrics.title || 'AI Song';",
    "        lyricsGenerated = true;",
    "      } else {",
    "        const desc = await understandImage(media);",
    "        promptForLyrics = `${desc}\\n\\n\u989d\u5916\u8981\u6c42\uff1a${input}`;",
    "      }",
    "    }",
    "    if (!lyricsGenerated) {",
    "      const lyr = await fetchLyrics(promptForLyrics);",
    "      lyricsText = lyr.text || promptForLyrics || input;",
    "      titleText = lyr.title || 'AI Song';",
    "    }",
    "    document.getElementById('lyrics').textContent = lyricsText;",
    "  }",
    "  lastLyricsText = lyricsText;",
    "  lastTitleText = titleText;",
]
old = "\n".join(old_lines) + "\n"
new = "\n".join(new_lines) + "\n"
if old not in text:
    raise SystemExit('not found block')
text = text.replace(old, new)
Path("maono.html").write_text(text.replace("\n", "\r\n"), encoding="utf-8")
