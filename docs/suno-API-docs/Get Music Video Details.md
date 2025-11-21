# Get Music Video Details

> Retrieve detailed information about a music video generation task, including status and download link.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/mp4/record-info
paths:
  path: /api/v1/mp4/record-info
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
                The task ID returned from the Create Music Video endpoint. Used
                to retrieve detailed information about the video generation
                task, including processing status and download URL.
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
                      musicId:
                        type: string
                        description: >-
                          The ID of the source music track that was converted to
                          video
                      callbackUrl:
                        type: string
                        description: >-
                          The callback URL that was provided in the video
                          generation request
                      audioId:
                        type: string
                        description: >-
                          The audio ID of the track within the original
                          generation task
                      completeTime:
                        type: string
                        description: The timestamp when the video generation was completed
                        format: date-time
                      response:
                        type: object
                        properties:
                          videoUrl:
                            type: string
                            description: The URL to download the generated MP4 video
                      successFlag:
                        type: string
                        description: The current status of the video generation task
                        enum:
                          - PENDING
                          - SUCCESS
                          - CREATE_TASK_FAILED
                          - GENERATE_MP4_FAILED
                          - CALLBACK_EXCEPTION
                      createTime:
                        type: string
                        description: Creation time
                        format: date-time
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
                taskId: taskId_774b9aa0422f
                musicId: audioId_0295980ec02e
                callbackUrl: https://api.example.com/callback
                audioId: e231****-****-****-****-****8cadc7dc
                completeTime: 1735661400000
                response:
                  videoUrl: https://example.com/videos/video_847715e66259.mp4
                successFlag: SUCCESS
                createTime: 1735661400000
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