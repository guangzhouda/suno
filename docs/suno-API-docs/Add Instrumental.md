# Add Instrumental

> This endpoint generates a musical accompaniment tailored to an uploaded audio file — typically a vocal stem or melody track. It helps users instantly flesh out their vocal ideas with high-quality backing music, all without needing a producer.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/add-instrumental
paths:
  path: /api/v1/generate/add-instrumental
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
              uploadUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL of the uploaded music file to add instrumental
                      to.  

                      - Required.  

                      - Must be a valid audio file URL accessible by the
                      system.  

                      - The uploaded audio should be in a supported format (MP3,
                      WAV, etc.).
                    example: https://example.com/music.mp3
              title:
                allOf:
                  - type: string
                    description: >-
                      The title of the music track.  

                      - Required.  

                      - This will be used as the title for the generated
                      instrumental track.
                    example: Relaxing Piano
              negativeTags:
                allOf:
                  - type: string
                    description: >-
                      Music styles or traits to exclude from the generated
                      instrumental.  

                      - Required.  

                      - Use to avoid specific styles or instruments in the
                      instrumental version.  
                        Example: "Heavy Metal, Aggressive Drums"
                    example: Heavy Metal, Aggressive Drums
              tags:
                allOf:
                  - type: string
                    description: >-
                      Music style and characteristics for the instrumental.  

                      - Required.  

                      - Describe the desired style, mood, and instruments for
                      the instrumental track.  
                        Example: "Relaxing Piano, Ambient, Peaceful"
                    example: Relaxing Piano, Ambient, Peaceful
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL to receive task completion notifications when
                      instrumental generation is complete. The callback process
                      has three stages: `text` (text generation), `first` (first
                      track complete), `complete` (all tracks complete). Note:
                      In some cases, `text` and `first` stages may be skipped,
                      directly returning `complete`.


                      For detailed callback format and implementation guide, see
                      [Add Instrumental Callbacks](./add-instrumental-callbacks)

                      - Alternatively, you can use the Get Music Generation
                      Details interface to poll task status
                    example: https://api.example.com/callback
              vocalGender:
                allOf:
                  - type: string
                    description: >-
                      Preferred vocal gender for any vocal elements. Optional.
                      Allowed values: 'm' (male), 'f' (female).
                    enum:
                      - m
                      - f
                    example: m
              styleWeight:
                allOf:
                  - type: number
                    description: >-
                      Style adherence weight. Optional. Range: 0-1. Two decimal
                      places recommended.
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.61
              weirdnessConstraint:
                allOf:
                  - type: number
                    description: >-
                      Creativity/novelty constraint. Optional. Range: 0-1. Two
                      decimal places recommended.
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.72
              audioWeight:
                allOf:
                  - type: number
                    description: >-
                      Relative weight of audio consistency versus other
                      controls. Optional. Range: 0-1. Two decimal places
                      recommended.
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              model:
                allOf:
                  - type: string
                    description: >-
                      Model version to use for generation. Optional. Default:
                      V4_5PLUS.
                    enum:
                      - V4_5PLUS
                      - V5
                    default: V4_5PLUS
                    example: V4_5PLUS
            required: true
            requiredProperties:
              - uploadUrl
              - title
              - negativeTags
              - tags
              - callBackUrl
        examples:
          example:
            value:
              uploadUrl: https://example.com/music.mp3
              title: Relaxing Piano
              negativeTags: Heavy Metal, Aggressive Drums
              tags: Relaxing Piano, Ambient, Peaceful
              callBackUrl: https://api.example.com/callback
              vocalGender: m
              styleWeight: 0.61
              weirdnessConstraint: 0.72
              audioWeight: 0.65
              model: V4_5PLUS
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