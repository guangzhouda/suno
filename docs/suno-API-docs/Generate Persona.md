# Generate Persona

> Create a personalized music Persona based on generated music, giving the music a unique identity and characteristics.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/generate-persona
paths:
  path: /api/v1/generate/generate-persona
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
                      Unique identifier of the original music generation task.
                      This can be a taskId returned from any of the following
                      endpoints:

                      - Generate Music (/api/v1/generate)

                      - Extend Music (/api/v1/generate/extend)

                      - Upload And Cover Audio (/api/v1/generate/upload-cover)

                      - Upload And Extend Audio (/api/v1/generate/upload-extend)
                    example: 5c79****be8e
              audioId:
                allOf:
                  - type: string
                    description: Audio ID of the music track to create Persona for.
                    example: e231****-****-****-****-****8cadc7dc
              name:
                allOf:
                  - type: string
                    description: >-
                      Name for the Persona. A descriptive name that captures the
                      essence of the musical style or character.
                    example: Electronic Pop Singer
              description:
                allOf:
                  - type: string
                    description: >-
                      Detailed description of the Persona's musical
                      characteristics, style, and personality. Be specific about
                      genre, mood, instrumentation, and vocal qualities.
                    example: >-
                      A modern electronic music style pop singer, skilled in
                      dynamic rhythms and synthesizer tones
            required: true
            requiredProperties:
              - taskId
              - audioId
              - name
              - description
        examples:
          example:
            value:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
              name: Electronic Pop Singer
              description: >-
                A modern electronic music style pop singer, skilled in dynamic
                rhythms and synthesizer tones
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
                      - 401
                      - 402
                      - 404
                      - 409
                      - 422
                      - 429
                      - 451
                      - 455
                      - 500
                    description: >-
                      Response Status Codes


                      - **200**: Success - Request has been processed
                      successfully  

                      - **401**: Unauthorized - Authentication credentials are
                      missing or invalid  

                      - **402**: Insufficient Credits - Account does not have
                      enough credits to perform the operation  

                      - **404**: Not Found - The requested resource or endpoint
                      does not exist  

                      - **409**: Conflict - Persona already exists for this
                      music

                      - **422**: Validation Error - The request parameters
                      failed validation checks  

                      - **429**: Rate Limited - Request limit has been exceeded
                      for this resource  

                      - **451**: Unauthorized - Failed to fetch the music data.
                      Kindly verify any access limits set by you or your service
                      provider  

                      - **455**: Service Unavailable - System is currently
                      undergoing maintenance  

                      - **500**: Server Error - An unexpected error occurred
                      while processing the request
              msg:
                allOf:
                  - type: string
                    description: Error message when code != 200
                    example: success
              data:
                allOf:
                  - type: object
                    properties:
                      personaId:
                        type: string
                        description: >-
                          Unique identifier for the generated Persona. This
                          personaId can be used in subsequent music generation
                          requests (Generate Music, Extend Music, Upload And
                          Cover Audio, Upload And Extend Audio) to create music
                          with similar style characteristics.
                        example: a1b2****c3d4
                      name:
                        type: string
                        description: Name of the Persona as provided in the request.
                        example: Electronic Pop Singer
                      description:
                        type: string
                        description: >-
                          Description of the Persona's musical characteristics,
                          style, and personality as provided in the request.
                        example: >-
                          A modern electronic music style pop singer, skilled in
                          dynamic rhythms and synthesizer tones
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                personaId: a1b2****c3d4
                name: Electronic Pop Singer
                description: >-
                  A modern electronic music style pop singer, skilled in dynamic
                  rhythms and synthesizer tones
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