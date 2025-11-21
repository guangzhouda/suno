# Extend Music

> Extend or modify existing music tracks.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/extend
paths:
  path: /api/v1/generate/extend
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
              defaultParamFlag:
                allOf:
                  - type: boolean
                    description: >-
                      Controls parameter usage mode.  

                      - `true`: Use custom parameters (requires `continueAt`,
                      `prompt`, `style`, and `title`).  

                      - `false`: Use original audio parameters (only `audioId`
                      is required).
                    example: true
              audioId:
                allOf:
                  - type: string
                    description: >-
                      Audio ID of the track to extend. This is the source track
                      that will be continued.
                    example: e231****-****-****-****-****8cadc7dc
              prompt:
                allOf:
                  - type: string
                    description: >-
                      Description of how the music should be extended. Required
                      when defaultParamFlag is true.
                    example: Extend the music with more relaxing notes
              style:
                allOf:
                  - type: string
                    description: Music style, e.g., Jazz, Classical, Electronic
                    example: Classical
              title:
                allOf:
                  - type: string
                    description: Music title
                    example: Peaceful Piano Extended
              continueAt:
                allOf:
                  - type: number
                    description: >-
                      The time point (in seconds) from which to start extending
                      the music.  

                      - Required when `defaultParamFlag` is `true`.  

                      - Value range: greater than 0 and less than the total
                      duration of the generated audio.  

                      - Specifies the position in the original track where the
                      extension should begin.
                    example: 60
              personaId:
                allOf:
                  - type: string
                    description: >-
                      Only available when Custom Mode (`customMode: true`) is
                      enabled. Persona ID to apply to the generated music.
                      Optional. Use this to apply a specific persona style to
                      your music generation. 


                      To generate a persona ID, use the [Generate
                      Persona](generate-persona) endpoint to create a
                      personalized music Persona based on generated music.
                    example: persona_123
              model:
                allOf:
                  - type: string
                    description: >-
                      Model version to use, must be consistent with the source
                      audio.  

                      - Available options:  
                        - **`V5`**: Superior musical expression, faster generation.  
                        - **`V4_5PLUS`**: V4.5+ is richer sound, new waysto create, max 8 min.  
                        - **`V4_5`**: V4.5 is smarter prompts, fastergenerations, max 8 min.  
                        - **`V4`**: V4 is improved vocal quality,max 4 min.  
                        - **`V3_5`**: V3.5 is better song structure,max 4 min.
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
                    description: Music styles to exclude from generation
                    example: Relaxing Piano
              vocalGender:
                allOf:
                  - type: string
                    description: Preferred vocal gender for generated vocals. Optional.
                    enum:
                      - m
                      - f
                    example: m
              styleWeight:
                allOf:
                  - type: number
                    description: Weight of the provided style guidance. Range 0.00–1.00.
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              weirdnessConstraint:
                allOf:
                  - type: number
                    description: Constraint on creative deviation/novelty. Range 0.00–1.00.
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              audioWeight:
                allOf:
                  - type: number
                    description: >-
                      Weight of the input audio influence (where applicable).
                      Range 0.00–1.00.
                    minimum: 0
                    maximum: 1
                    multipleOf: 0.01
                    example: 0.65
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL to receive task completion notifications when
                      music extension is complete.


                      For detailed callback format and implementation guide, see
                      [Music Extension Callbacks](./extend-music-callbacks)

                      - Alternatively, you can use the get music generation
                      details endpoint to poll task status
                    example: https://api.example.com/callback
            required: true
            requiredProperties:
              - defaultParamFlag
              - audioId
              - callBackUrl
              - model
        examples:
          example:
            value:
              defaultParamFlag: true
              audioId: e231****-****-****-****-****8cadc7dc
              prompt: Extend the music with more relaxing notes
              style: Classical
              title: Peaceful Piano Extended
              continueAt: 60
              personaId: persona_123
              model: V3_5
              negativeTags: Relaxing Piano
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