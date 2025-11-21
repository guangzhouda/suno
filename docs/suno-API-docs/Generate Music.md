# 生成音乐

> 使用AI模型生成带有或不带歌词的音乐。

## OpenAPI

````yaml cn/suno-api/suno-api-cn.json post /api/v1/generate
paths:
  path: /api/v1/generate
  method: post
  servers:
    - url: https://api.sunoapi.org
      description: API 服务器
  request:
    security:
      - title: BearerAuth
        parameters:
          query: {}
          header:
            Authorization:
              type: http
              scheme: bearer
              description: |-
                # 🔑 API 认证说明

                所有接口都需要通过 Bearer Token 方式进行认证。

                ## 获取 API Key

                1. 访问 [API Key 管理页面](https://sunoapi.org/api-key) 获取您的 API Key

                ## 使用方式

                在请求头中添加：

                ```
                Authorization: Bearer YOUR_API_KEY
                ```

                > **⚠️ 注意：**
                > - 请妥善保管您的 API Key，不要泄露给他人
                > - 如果怀疑 API Key 泄露，请立即在管理页面重置
          cookie: {}
    parameters:
      path: {}
      query: {}
      header: {}
      cookie: {}
    body:
      application/json:
        schemaArray:
          - type: object
            properties:
              prompt:
                allOf:
                  - type: string
                    description: >-
                      描述所需音频内容的提示词。  

                      - 自定义模式下（`customMode: true`）：当 `instrumental` 为 `false`
                      时必填。提示词将严格作为歌词使用并在生成的音轨中演唱。不同模型的字符限制：  
                        - **V3_5 和 V4**：最多3000字符  
                        - **V4_5、V4_5PLUS 和 V5**：最多5000字符  
                        示例："一段平静舒缓的钢琴曲，带有柔和的旋律"  
                      - 非自定义模式下（`customMode:
                      false`）：始终必填。提示词作为核心创意，歌词将根据它自动生成（不严格匹配输入），最多500字符。  
                        
                        示例："一段简短放松的钢琴曲"
                    example: 一段平静舒缓的钢琴曲，带有柔和的旋律
              style:
                allOf:
                  - type: string
                    description: |-
                      音乐风格或流派。  
                      - 在自定义模式下（`customMode: true`）必填。示例："爵士"、"古典"、"电子"。
                        - 对于 V3_5 和 V4 模型：最大长度：200字符。
                        - 对于 V4_5、V4_5PLUS 和 V5 模型：最大长度：1000字符。
                        示例："古典"  
                      - 在非自定义模式下（`customMode: false`）：留空。
                    example: 古典
              title:
                allOf:
                  - type: string
                    description: |-
                      生成音乐的标题。  
                      - 在自定义模式下（`customMode: true`）必填。最大长度：80字符。  
                        示例："宁静钢琴冥想"  
                      - 在非自定义模式下（`customMode: false`）：留空。
                    example: 宁静钢琴冥想
              customMode:
                allOf:
                  - type: boolean
                    description: >-
                      启用自定义模式进行高级音频生成设置。  

                      - 设为 `true` 使用自定义模式（需要提供 `style` 和 `title`；如果
                      `instrumental` 为 `false`，则需要提供 `prompt`）。如果 `instrumental`
                      为 `false`，提示词将严格用作歌词。  

                      - 设为 `false` 使用非自定义模式（只需要提供 `prompt`）。歌词将根据提示词自动生成。
                    example: true
              instrumental:
                allOf:
                  - type: boolean
                    description: >-
                      决定音频是否为纯音乐（无歌词）。  

                      - 在自定义模式下（`customMode: true`）：  
                        - 如果为 `true`：只需提供 `style` 和 `title`。  
                        - 如果为 `false`：需要提供 `style`、`title` 和 `prompt`（`prompt` 将作为精确歌词使用）。  
                      - 在非自定义模式下（`customMode: false`）：不影响必填字段（只需 `prompt`）。如果为
                      `false`，将自动生成歌词。
                    example: true
              personaId:
                allOf:
                  - type: string
                    description: >-
                      仅在开启自定义模式（`customMode:
                      true`）时可用。应用到生成音乐的人格ID。可选。使用此参数为音乐生成应用特定的人格风格。 


                      要生成人格ID，请使用 [生成 Persona](generate-persona)
                      接口，基于已生成的音乐创建个性化的音乐人格。
                    example: persona_123
              model:
                allOf:
                  - type: string
                    description: |-
                      使用的模型版本，必须与源音频保持一致。  
                      - 可选择：  
                        - **`v5`**: 更卓越的音乐表现力，生成速度更快。  
                        - **`V4_5PLUS`**: V4.5+ 音色更丰富，新的创作方式，最长8分钟。  
                        - **`V4_5`**: V4.5 更智能的提示词，更快的生成速度，最长8分钟。  
                        - **`V4`**: V4 改进的人声质量，最长4分钟。  
                        - **`V3_5`**: V3.5 更好的歌曲结构，最长4分钟。
                    enum:
                      - V3_5
                      - V4
                      - V4_5
                      - V4_5PLUS
                      - V5
                    example: V3_5
              negativeTags:
                allOf:
                  - type: string
                    description: |-
                      需要在生成的音频中排除的音乐风格或特征。  
                      - 可选。用于避免特定风格。  
                        示例："重金属, 强节奏鼓点"
                    example: 重金属, 强节奏鼓点
              vocalGender:
                allOf:
                  - type: string
                    description: 期望的人声性别（可选）
                    enum:
                      - m
                      - f
                    example: m
              styleWeight:
                allOf:
                  - type: number
                    description: 风格指引权重，范围 0.00–1.00
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              weirdnessConstraint:
                allOf:
                  - type: number
                    description: 创意发散/奇异度约束，范围 0.00–1.00
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              audioWeight:
                allOf:
                  - type: number
                    description: 输入音频影响力权重（如适用），范围 0.00–1.00
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      接收任务完成通知的URL。回调过程有三个阶段：`text`（文本生成）、`first`（第一首完成）、`complete`（全部完成）。注意：某些情况下可能会跳过
                      `text` 和 `first` 阶段，直接返回 `complete`。


                      详细的回调格式和实现指南，请参见 [音乐生成回调](./generate-music-callbacks)

                      - 或者，您也可以使用获取音乐生成详情接口来轮询任务状态
                    example: https://api.example.com/callback
            required: true
            requiredProperties:
              - customMode
              - instrumental
              - callBackUrl
              - model
        examples:
          example:
            value:
              prompt: 一段平静舒缓的钢琴曲，带有柔和的旋律
              style: 古典
              title: 宁静钢琴冥想
              customMode: true
              instrumental: true
              personaId: persona_123
              model: V3_5
              negativeTags: 重金属, 强节奏鼓点
              vocalGender: m
              styleWeight: 0.65
              weirdnessConstraint: 0.65
              audioWeight: 0.65
              callBackUrl: https://api.example.com/callback
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              code:
                allOf:
                  - type: integer
                    description: |-
                      # 状态码说明

                      - ✅ 200 - 请求成功
                      - ⚠️ 400 - 参数错误
                      - ⚠️ 401 - 没有访问权限
                      - ⚠️ 404 - 请求方式或者路径错误
                      - ⚠️ 405 - 调用超过限制
                      - ⚠️ 413 - 主题或者prompt过长
                      - ⚠️ 429 - 积分不足
                      - ⚠️ 430 - 您的调用频率过高，请稍后再试。
                      - ⚠️ 455 - 网站维护
                      - ❌ 500 - 服务器异常
                    example: 200
                    enum:
                      - 200
                      - 400
                      - 401
                      - 404
                      - 405
                      - 413
                      - 429
                      - 430
                      - 455
                      - 500
              msg:
                allOf:
                  - type: string
                    description: 当 code != 200 时，展示错误信息
                    example: success
              data:
                allOf:
                  - type: object
                    properties:
                      taskId:
                        type: string
                        description: 任务ID，用于后续查询任务状态
                        example: 5c79****be8e
            refIdentifier: '#/components/schemas/ApiResponse'
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: 5c79****be8e
        description: 请求成功
    '500':
      _mintlify/placeholder:
        schemaArray:
          - type: any
            description: 服务器异常
        examples: {}
        description: 服务器异常
  deprecated: false
  type: path
components:
  schemas: {}

````

