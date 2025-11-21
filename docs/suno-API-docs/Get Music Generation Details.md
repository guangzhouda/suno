# Get Music Generation Details

> Retrieve detailed information about a music generation task, including status, parameters, and results.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/generate/record-info
paths:
  path: /api/v1/generate/record-info
  method: get
  servers:
    - url: https://api.sunoapi.org
      description: API Server
  request:
    security:
      - title: BearerAuth
        parameters:
          query: {}
          header:
            Authorization:
              type: http
              scheme: bearer
              description: >-
                # 🔑 API Authentication


                All endpoints require authentication using Bearer Token.


                ## Get API Key


                1. Visit the [API Key Management
                Page](https://sunoapi.org/api-key) to obtain your API Key


                ## Usage


                Add to request headers:


                ```

                Authorization: Bearer YOUR_API_KEY

                ```


                > **⚠️ Note:**

                > - Keep your API Key secure and do not share it with others

                > - If you suspect your API Key has been compromised, reset it
                immediately from the management page
          cookie: {}
    parameters:
      path: {}
      query:
        taskId:
          schema:
            - type: string
              required: true
              description: >-
                The task ID returned from the Generate Music or Extend Music
                endpoints. Used to identify the specific generation task to
                query.
      header: {}
      cookie: {}
    body: {}
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              code:
                allOf:
                  - type: integer
                    description: >-
                      # Status Codes


                      - ✅ 200 - Request successful

                      - ⚠️ 400 - Invalid parameters

                      - ⚠️ 401 - Unauthorized access

                      - ⚠️ 404 - Invalid request method or path

                      - ⚠️ 405 - Rate limit exceeded

                      - ⚠️ 413 - Theme or prompt too long

                      - ⚠️ 429 - Insufficient credits

                      - ⚠️ 430 - Your call frequency is too high. Please try
                      again later. 

                      - ⚠️ 455 - System maintenance

                      - ❌ 500 - Server error
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
                    description: Error message when code != 200
                    example: success
              data:
                allOf:
                  - type: object
                    properties:
                      taskId:
                        type: string
                        description: Task ID
                      parentMusicId:
                        type: string
                        description: Parent music ID (only valid when extending music)
                      param:
                        type: string
                        description: Parameter information for task generation
                      response:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Task ID
                          sunoData:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                  description: Audio unique identifier (audioId)
                                audioUrl:
                                  type: string
                                  description: Audio file URL
                                streamAudioUrl:
                                  type: string
                                  description: Streaming audio URL
                                imageUrl:
                                  type: string
                                  description: Cover image URL
                                prompt:
                                  type: string
                                  description: Generation prompt/lyrics
                                modelName:
                                  type: string
                                  description: Model name used
                                title:
                                  type: string
                                  description: Music title
                                tags:
                                  type: string
                                  description: Music tags
                                createTime:
                                  type: string
                                  description: Creation time
                                  format: date-time
                                duration:
                                  type: number
                                  description: Audio duration (seconds)
                      status:
                        type: string
                        description: Task status
                        enum:
                          - PENDING
                          - TEXT_SUCCESS
                          - FIRST_SUCCESS
                          - SUCCESS
                          - CREATE_TASK_FAILED
                          - GENERATE_AUDIO_FAILED
                          - CALLBACK_EXCEPTION
                          - SENSITIVE_WORD_ERROR
                      type:
                        type: string
                        enum:
                          - chirp-v3-5
                          - chirp-v4
                        description: Task type
                      operationType:
                        type: string
                        enum:
                          - generate
                          - extend
                          - upload_cover
                          - upload_extend
                        description: >-
                          Operation Type


                          - `generate`: Generate Music - Create new music works
                          using AI model

                          - `extend`: Extend Music - Extend or modify existing
                          music works

                          - `upload_cover`: Upload And Cover Audio - Create new
                          music works based on uploaded audio files

                          - `upload_extend`: Upload And Extend Audio - Extend or
                          modify music works based on uploaded audio files
                      errorCode:
                        type: number
                        description: Error code, valid when task fails
                      errorMessage:
                        type: string
                        description: Error message, valid when task fails
            refIdentifier: '#/components/schemas/ApiResponse'
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: 5c79****be8e
                parentMusicId: ''
                param: >-
                  {"prompt":"A calm piano
                  track","style":"Classical","title":"Peaceful
                  Piano","customMode":true,"instrumental":true,"model":"V3_5"}
                response:
                  taskId: 5c79****be8e
                  sunoData:
                    - id: 8551****662c
                      audioUrl: https://example.cn/****.mp3
                      streamAudioUrl: https://example.cn/****
                      imageUrl: https://example.cn/****.jpeg
                      prompt: '[Verse] 夜晚城市 灯火辉煌'
                      modelName: chirp-v3-5
                      title: 钢铁侠
                      tags: electrifying, rock
                      createTime: '2025-01-01 00:00:00'
                      duration: 198.44
                status: SUCCESS
                type: GENERATE
                errorCode: null
                errorMessage: null
        description: Request successful
    '500':
      _mintlify/placeholder:
        schemaArray:
          - type: any
            description: Server error
        examples: {}
        description: Server error
  deprecated: false
  type: path
components:
  schemas: {}

````