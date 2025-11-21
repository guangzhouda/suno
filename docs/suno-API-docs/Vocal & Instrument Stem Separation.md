# Vocal & Instrument Stem Separation

> Use Suno’s official get‑stem API to split tracks created on our platform into clean vocal, accompaniment, or per‑instrument stems with state‑of‑the‑art source‑separation AI.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/vocal-removal/generate
paths:
  path: /api/v1/vocal-removal/generate
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
                      to be processed.  

                      - Both `taskId` and `audioId` are needed for accurate
                      track identification.
                    example: 5c79****be8e
              audioId:
                allOf:
                  - type: string
                    description: >-
                      The ID of the specific audio track to separate.  

                      - Required. This identifies which specific track within
                      the task to process.  

                      - Both `taskId` and `audioId` are needed for accurate
                      track identification.
                    example: e231****-****-****-****-****8cadc7dc
              type:
                allOf:
                  - type: string
                    description: >-
                      Separation type.  

                      - `separate_vocal`: Separate vocals and accompaniment,
                      generating vocal track and instrumental track (default)  

                      - `split_stem`: Separate various instrument sounds,
                      generating vocals, backing vocals, drums, bass, guitar,
                      keyboard, strings, brass, woodwinds, percussion,
                      synthesizer, effects and other tracks
                    enum:
                      - separate_vocal
                      - split_stem
                    default: separate_vocal
                    example: separate_vocal
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL to receive vocal separation results when
                      processing is complete.  

                      - Required.  

                      - The callback will include multiple URLs: original audio,
                      isolated vocals, instrumental track, and individual
                      instrument tracks.


                      For detailed callback format and implementation guide, see
                      [Vocal Separation
                      Callbacks](./separate-vocals-from-music-callbacks)

                      - Alternatively, you can use the get vocal separation
                      details endpoint to poll task status
                    example: https://api.example.com/callback
            required: true
            requiredProperties:
              - taskId
              - audioId
              - callBackUrl
        examples:
          example:
            value:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
              type: separate_vocal
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
                        description: Task ID for tracking task status
                        example: 5c79****be8e
            refIdentifier: '#/components/schemas/ApiResponse'
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: 5c79****be8e
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