# Get Timestamped Lyrics

> Retrieve timestamped lyrics for synchronized display during audio playback.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/get-timestamped-lyrics
paths:
  path: /api/v1/generate/get-timestamped-lyrics
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
                      The task ID of the music generation task. Required to
                      identify which generation task contains the lyrics.
                    example: 5c79****be8e
              audioId:
                allOf:
                  - type: string
                    description: Audio ID of the track to retrieve lyrics for.
                    example: e231****-****-****-****-****8cadc7dc
            required: true
            requiredProperties:
              - taskId
              - audioId
        examples:
          example:
            value:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
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
                      alignedWords:
                        type: array
                        description: List of aligned lyrics words
                        items:
                          type: object
                          properties:
                            word:
                              type: string
                              description: Lyrics word
                              example: |-
                                [Verse]
                                Waggin'
                            success:
                              type: boolean
                              description: Whether lyrics word is successfully aligned
                              example: true
                            startS:
                              type: number
                              description: Word start time (seconds)
                              example: 1.36
                            endS:
                              type: number
                              description: Word end time (seconds)
                              example: 1.79
                            palign:
                              type: integer
                              description: Alignment parameter
                              example: 0
                      waveformData:
                        type: array
                        description: Waveform data, used for audio visualization
                        items:
                          type: number
                        example:
                          - 0
                          - 1
                          - 0.5
                          - 0.75
                      hootCer:
                        type: number
                        description: Lyrics alignment accuracy score
                        example: 0.3803191489361702
                      isStreamed:
                        type: boolean
                        description: Whether it's streaming audio
                        example: false
            refIdentifier: '#/components/schemas/ApiResponse'
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                alignedWords:
                  - word: |-
                      [Verse]
                      Waggin'
                    success: true
                    startS: 1.36
                    endS: 1.79
                    palign: 0
                waveformData:
                  - 0
                  - 1
                  - 0.5
                  - 0.75
                hootCer: 0.3803191489361702
                isStreamed: false
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