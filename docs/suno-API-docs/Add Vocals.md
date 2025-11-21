# Add Vocals

> This endpoint layers AI-generated vocals on top of an existing instrumental. Given a prompt (e.g., lyrical concept or musical mood) and optional audio, it produces vocal output harmonized with the provided track.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/add-vocals
paths:
  path: /api/v1/generate/add-vocals
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
              prompt:
                allOf:
                  - type: string
                    description: >-
                      Description of the audio content to generate vocals for.  

                      - Required.  

                      - Provides context about the desired vocal style and
                      content.  

                      - The more detailed your prompt, the better the vocal
                      generation will match your vision.
                    example: A calm and relaxing piano track with soothing vocals
              title:
                allOf:
                  - type: string
                    description: >-
                      The title of the music track.  

                      - Required.  

                      - This will be used as the title for the generated vocal
                      track.
                    example: Relaxing Piano with Vocals
              negativeTags:
                allOf:
                  - type: string
                    description: >-
                      Music styles or vocal traits to exclude from the generated
                      track.  

                      - Required.  

                      - Use to avoid specific vocal styles or characteristics.  
                        Example: "Heavy Metal, Aggressive Vocals"
                    example: Heavy Metal, Aggressive Vocals
              style:
                allOf:
                  - type: string
                    description: |-
                      The music and vocal style.  
                      - Required.  
                      - Examples: "Jazz", "Classical", "Electronic", "Pop".  
                      - Describes the overall genre and vocal approach.
                    example: Jazz
              vocalGender:
                allOf:
                  - type: string
                    description: >-
                      Preferred vocal gender. Optional. Allowed values: 'm'
                      (male), 'f' (female).
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
              uploadUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL of the uploaded audio file to add vocals to.  

                      - Required.  

                      - Must be a valid audio file URL accessible by the
                      system.  

                      - The uploaded audio should be in a supported format (MP3,
                      WAV, etc.).
                    example: https://example.com/instrumental.mp3
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      The URL to receive task completion notifications when
                      vocal generation is complete. The callback process has
                      three stages: `text` (text generation), `first` (first
                      track complete), `complete` (all tracks complete). Note:
                      In some cases, `text` and `first` stages may be skipped,
                      directly returning `complete`.


                      For detailed callback format and implementation guide, see
                      [Add Vocals Callbacks](./add-vocals-callbacks)

                      - Alternatively, you can use the Get Music Generation
                      Details interface to poll task status
                    example: https://api.example.com/callback
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
              - callBackUrl
              - prompt
              - title
              - negativeTags
              - style
        examples:
          example:
            value:
              prompt: A calm and relaxing piano track with soothing vocals
              title: Relaxing Piano with Vocals
              negativeTags: Heavy Metal, Aggressive Vocals
              style: Jazz
              vocalGender: m
              styleWeight: 0.61
              weirdnessConstraint: 0.72
              audioWeight: 0.65
              uploadUrl: https://example.com/instrumental.mp3
              callBackUrl: https://api.example.com/callback
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