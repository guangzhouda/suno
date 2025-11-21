# Create Music Video

> Generate an MP4 video with visualizations for a music track.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/mp4/generate
paths:
  path: /api/v1/mp4/generate
  method: post
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
      query: {}
      header: {}
      cookie: {}
    body:
      application/json:
        schemaArray:
          - type: object
            properties:
              taskId:
                allOf:
                  - type: string
                    description: >-
                      The task ID of the music generation task.  

                      - Required. This identifies the task containing the audio
                      to be converted to video.  

                      - Both `taskId` and `audioId` are needed to identify the
                      exact track.
                    example: taskId_774b9aa0422f
              audioId:
                allOf:
                  - type: string
                    description: >-
                      The ID of the specific track to convert to video.  

                      - Required. This identifies which specific track within
                      the task to convert.  

                      - Both `taskId` and `audioId` are needed to identify the
                      exact track.
                    example: e231****-****-****-****-****8cadc7dc
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL to receive video generation completion
                      notification.  

                      - Required.  

                      - The callback will include a single downloadable URL for
                      the generated MP4 video.


                      For detailed callback format and implementation guide, see
                      [Music Video Generation
                      Callbacks](./create-music-video-callbacks)

                      - Alternatively, you can use the get music video details
                      endpoint to poll task status
                    example: https://api.example.com/callback
              author:
                allOf:
                  - type: string
                    maxLength: 50
                    description: >-
                      The artist or creator name to display on the video.  

                      - Optional.  

                      - Will be shown prominently in the video, typically at the
                      beginning.  

                      - Maximum 50 characters.
                    example: Suno Artist
              domainName:
                allOf:
                  - type: string
                    maxLength: 50
                    description: >-
                      The website or brand to display as watermark.  

                      - Optional.  

                      - Will appear as a subtle watermark at the bottom of the
                      video.  

                      - Maximum 50 characters.
                    example: music.example.com
            required: true
            requiredProperties:
              - taskId
              - audioId
              - callBackUrl
        examples:
          example:
            value:
              taskId: taskId_774b9aa0422f
              audioId: e231****-****-****-****-****8cadc7dc
              callBackUrl: https://api.example.com/callback
              author: Suno Artist
              domainName: music.example.com
  response:
    '200':
      application/json:
        schemaArray:
          - type: object
            properties:
              code:
                allOf:
                  - type: integer
                    enum:
                      - 200
                      - 400
                      - 401
                      - 404
                      - 405
                      - 409
                      - 413
                      - 429
                      - 430
                      - 455
                      - 500
                    description: >-
                      # Status Codes


                      - ✅ 200 - Request successful

                      - ⚠️ 400 - Invalid parameters

                      - ⚠️ 401 - Unauthorized access

                      - ⚠️ 404 - Invalid request method or path

                      - ⚠️ 405 - Rate limit exceeded

                      - ⚠️ 409 - Conflict - Mp4 record already exists

                      - ⚠️ 413 - Theme or prompt too long

                      - ⚠️ 429 - Insufficient credits

                      - ⚠️ 430 - Your call frequency is too high. Please try
                      again later. 

                      - ⚠️ 455 - System maintenance

                      - ❌ 500 - Server error
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
                        description: Task ID for tracking task status
                        example: taskId_774b9aa0422f
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: taskId_774b9aa0422f
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