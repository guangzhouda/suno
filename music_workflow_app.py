"""
AI 音乐创作工作流 - Web 应用
集成 DeepSeek + Suno 的完整音乐创作系统
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# 导入路由
from modules.routes import music_workflow_router
from config import get_config

# 创建应用
app = FastAPI(
    title="AI音乐创作工作流",
    description="DeepSeek + Suno 智能音乐创作系统",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(music_workflow_router)

# Web 界面
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI音乐创作工作流</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        .templates-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .template-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .template-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }

        .template-card.active {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea15, #764ba215);
        }

        .template-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .template-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 8px;
        }

        .template-description {
            font-size: 0.9rem;
            color: #718096;
            line-height: 1.5;
        }

        .input-section {
            margin-top: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #2d3748;
        }

        .form-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea.form-input {
            min-height: 120px;
            resize: vertical;
        }

        .button {
            padding: 14px 32px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .button-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .button-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .button-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result-section {
            margin-top: 40px;
            padding-top: 40px;
            border-top: 2px solid #e2e8f0;
            display: none;
        }

        .result-section.show {
            display: block;
        }

        .lyrics-display {
            background: #f7fafc;
            border-radius: 12px;
            padding: 30px;
            margin-top: 20px;
        }

        .lyrics-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 20px;
        }

        .lyrics-metadata {
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }

        .metadata-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .metadata-label {
            font-weight: 600;
            color: #4a5568;
        }

        .metadata-value {
            color: #718096;
        }

        .lyrics-text {
            white-space: pre-wrap;
            line-height: 2;
            font-size: 1.05rem;
            color: #2d3748;
        }

        .alert {
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .alert-success {
            background: #c6f6d5;
            border: 1px solid #9ae6b4;
            color: #22543d;
        }

        .alert-error {
            background: #fed7d7;
            border: 1px solid #fc8181;
            color: #742a2a;
        }

        .loading {
            text-align: center;
            padding: 40px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .additional-fields {
            display: none;
        }

        .additional-fields.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 AI音乐创作工作流</h1>
            <p>DeepSeek V3 + Suno API - 从灵感到成曲，一站式创作</p>
        </div>

        <div class="main-card">
            <!-- 模板选择 -->
            <h2 style="margin-bottom: 20px;">选择创作模式</h2>
            <div class="templates-grid" id="templatesGrid">
                <!-- 模板卡片将通过 JS 动态加载 -->
            </div>

            <!-- 输入区域 -->
            <div class="input-section">
                <div class="form-group">
                    <label class="form-label">💭 你的想法或灵感</label>
                    <textarea
                        class="form-input"
                        id="userInput"
                        placeholder="例如：想写一首关于跨年夜独自在城市街头的歌，有点孤独但也有对新年的期待..."
                    ></textarea>
                </div>

                <!-- 额外字段（用于特定模板） -->
                <div id="additionalFields" class="additional-fields">
                    <div class="form-group">
                        <label class="form-label">原歌词</label>
                        <textarea class="form-input" id="originalLyrics" placeholder="输入需要改写或续写的歌词..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label">目标主题/风格</label>
                        <input type="text" class="form-input" id="targetTheme" placeholder="例如：温暖治愈">
                    </div>
                </div>

                <button class="button button-primary" id="generateBtn" onclick="generateLyrics()">
                    ✨ 开始创作
                </button>
            </div>

            <!-- 结果显示 -->
            <div class="result-section" id="resultSection">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>

    <script>
        let selectedTemplate = 'inspiration_songwriting';
        let templates = [];
        let currentLyricsData = null;
        let currentLyricsText = '';

        // 页面加载时获取模板列表
        async function loadTemplates() {
            try {
                const response = await fetch('/api/music-workflow/templates');
                const data = await response.json();

                if (data.code === 200) {
                    templates = data.data.templates;
                    renderTemplates();
                }
            } catch (error) {
                console.error('加载模板失败:', error);
            }
        }

        // 渲染模板卡片
        function renderTemplates() {
            const grid = document.getElementById('templatesGrid');
            grid.innerHTML = '';

            templates.forEach(template => {
                const card = document.createElement('div');
                card.className = 'template-card';
                if (template.id === selectedTemplate) {
                    card.classList.add('active');
                }

                card.innerHTML = `
                    <div class="template-icon">${template.icon}</div>
                    <div class="template-name">${template.name}</div>
                    <div class="template-description">${template.description}</div>
                `;

                card.onclick = () => selectTemplate(template.id);
                grid.appendChild(card);
            });
        }

        // 选择模板
        function selectTemplate(templateId) {
            selectedTemplate = templateId;
            renderTemplates();

            // 根据模板显示/隐藏额外字段
            const additionalFields = document.getElementById('additionalFields');
            const needsAdditional = ['lyrics_rewrite', 'style_transfer', 'continue_writing'];

            if (needsAdditional.includes(templateId)) {
                additionalFields.classList.add('show');
            } else {
                additionalFields.classList.remove('show');
            }
        }

        // 生成歌词
        async function generateLyrics() {
            const userInput = document.getElementById('userInput').value.trim();

            if (!userInput) {
                alert('请输入你的想法或灵感！');
                return;
            }

            const btn = document.getElementById('generateBtn');
            const resultSection = document.getElementById('resultSection');
            const resultContent = document.getElementById('resultContent');

            // 显示加载状态
            btn.disabled = true;
            btn.textContent = '🎨 创作中...';
            resultSection.classList.add('show');
            resultContent.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>DeepSeek V3 正在为你创作...</p>
                </div>
            `;

            try {
                // 构建请求数据
                const requestData = {
                    template: selectedTemplate,
                    user_input: userInput,
                    auto_generate_music: false  // 暂时不自动生成音乐
                };

                // 添加额外字段
                const originalLyrics = document.getElementById('originalLyrics').value.trim();
                const targetTheme = document.getElementById('targetTheme').value.trim();

                if (originalLyrics) {
                    requestData.original_lyrics = originalLyrics;
                }
                if (targetTheme) {
                    requestData.target_theme = targetTheme;
                    requestData.target_style = targetTheme;
                    requestData.mode = 'change_theme';
                }

                // 发送请求
                const response = await fetch('/api/music-workflow/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });

                const result = await response.json();

                if (result.success) {
                    displayLyrics(result);
                } else {
                    displayError(result.error || '创作失败');
                }
            } catch (error) {
                displayError('请求失败: ' + error.message);
            } finally {
                btn.disabled = false;
                btn.textContent = '✨ 开始创作';
            }
        }

        // 显示歌词
        function displayLyrics(result) {
            const resultContent = document.getElementById('resultContent');
            const lyricsData = result.lyrics_data;

            // 存储数据供生成音乐使用
            currentLyricsData = lyricsData;
            currentLyricsText = result.lyrics_text || '';

            const html = `
                <div class="alert alert-success">
                    ✅ 创作完成！
                </div>

                <div class="lyrics-display">
                    <div class="lyrics-title">${lyricsData.title || '生成的歌词'}</div>

                    <div class="lyrics-metadata">
                        ${lyricsData.theme ? `
                            <div class="metadata-item">
                                <span class="metadata-label">主题:</span>
                                <span class="metadata-value">${lyricsData.theme}</span>
                            </div>
                        ` : ''}

                        ${lyricsData.emotion ? `
                            <div class="metadata-item">
                                <span class="metadata-label">情绪:</span>
                                <span class="metadata-value">${lyricsData.emotion}</span>
                            </div>
                        ` : ''}

                        ${lyricsData.style ? `
                            <div class="metadata-item">
                                <span class="metadata-label">风格:</span>
                                <span class="metadata-value">${lyricsData.style}</span>
                            </div>
                        ` : ''}

                        ${lyricsData.recommended_model ? `
                            <div class="metadata-item">
                                <span class="metadata-label">推荐模型:</span>
                                <span class="metadata-value">${lyricsData.recommended_model}</span>
                            </div>
                        ` : ''}
                    </div>

                    ${lyricsData.reasoning ? `
                        <div style="margin-bottom: 25px; padding: 15px; background: white; border-radius: 8px;">
                            <div style="font-weight: 600; margin-bottom: 8px; color: #4a5568;">💡 创作思路</div>
                            <div style="color: #718096; line-height: 1.6;">${lyricsData.reasoning}</div>
                        </div>
                    ` : ''}

                    <div class="lyrics-text">${result.lyrics_text || JSON.stringify(lyricsData, null, 2)}</div>
                </div>

                <div style="margin-top: 20px; text-align: center;">
                    <button class="button button-primary" onclick="copyLyrics()">📋 复制歌词</button>
                    <button class="button button-primary" style="margin-left: 10px;" onclick="generateMusic()">🎵 生成音乐</button>
                    <button class="button button-primary" style="margin-left: 10px;" onclick="generateAgain()">🔄 重新生成</button>
                </div>

                <div id="musicResult" style="margin-top: 20px; display: none;"></div>
            `;

            resultContent.innerHTML = html;
        }

        // 显示错误
        function displayError(message) {
            const resultContent = document.getElementById('resultContent');
            resultContent.innerHTML = `
                <div class="alert alert-error">
                    ❌ ${message}
                </div>
            `;
        }

        // 复制歌词
        function copyLyrics() {
            const lyricsText = document.querySelector('.lyrics-text').textContent;
            navigator.clipboard.writeText(lyricsText).then(() => {
                alert('✅ 歌词已复制到剪贴板！');
            });
        }

        // 重新生成
        function generateAgain() {
            document.getElementById('resultSection').classList.remove('show');
            document.getElementById('userInput').value = '';
            document.getElementById('userInput').focus();
        }

        // 生成音乐
        async function generateMusic() {
            if (!currentLyricsText) {
                alert('请先生成歌词！');
                return;
            }

            const musicResult = document.getElementById('musicResult');
            musicResult.style.display = 'block';
            musicResult.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>🎵 Suno 正在生成音乐，请耐心等待（可能需要1-3分钟）...</p>
                </div>
            `;

            try {
                const title = currentLyricsData?.title || '未命名歌曲';
                const style = currentLyricsData?.style || 'pop';
                const tags = currentLyricsData?.tags?.join(', ') || style;

                // 调用 Suno API（假设 ai_platform.py 运行在 8000 端口）
                const response = await fetch('http://localhost:8000/api/suno/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: tags,
                        lyrics: currentLyricsText,
                        title: title,
                        model: 'V4',
                        wait: false
                    })
                });

                const result = await response.json();

                if (result.code === 200 || result.task_id) {
                    musicResult.innerHTML = `
                        <div class="alert alert-success">
                            🎵 音乐生成任务已提交！
                        </div>
                        <div style="background: #f7fafc; padding: 20px; border-radius: 12px;">
                            <p><strong>任务ID:</strong> ${result.task_id || result.data?.task_id || 'N/A'}</p>
                            <p style="color: #718096; margin-top: 10px;">
                                音乐生成需要1-3分钟，请前往 <a href="http://localhost:8000" target="_blank">主平台</a> 查看结果。
                            </p>
                        </div>
                    `;
                } else {
                    musicResult.innerHTML = `
                        <div class="alert alert-error">
                            ❌ 音乐生成失败: ${result.message || result.error || JSON.stringify(result)}
                        </div>
                    `;
                }
            } catch (error) {
                musicResult.innerHTML = `
                    <div class="alert alert-error">
                        ❌ 请求失败: ${error.message}<br>
                        <small>请确保 ai_platform.py 正在运行（端口8000）</small>
                    </div>
                `;
            }
        }

        // 初始化
        loadTemplates();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    """Web 界面"""
    return HTML_CONTENT

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "Music Workflow"}

if __name__ == "__main__":
    import uvicorn

    config = get_config()
    port = config.get('server.port', 8000) + 100  # 使用不同的端口避免冲突

    logger.info("="*60)
    logger.info("🎵 启动 AI 音乐创作工作流")
    logger.info("="*60)
    logger.info(f"Web界面: http://0.0.0.0:{port}")
    logger.info(f"API文档: http://0.0.0.0:{port}/docs")
    logger.info("="*60)

    uvicorn.run(
        "music_workflow_app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
