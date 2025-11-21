# Replace Music Section

> Replace a specific time segment within existing music.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/generate/replace-section
paths:
  path: /api/v1/generate/replace-section
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
                      Original task ID (parent task), used to identify the
                      source music for section replacement
                    example: 2fac****9f72
              audioId:
                allOf:
                  - type: string
                    description: Audio ID of the track to replace.
                    example: e231****-****-****-****-****8cadc7dc
              prompt:
                allOf:
                  - type: string
                    description: >-
                      Prompt for generating the replacement segment, typically
                      text describing the audio content
                    example: A calm and relaxing piano track.
              tags:
                allOf:
                  - type: string
                    description: Music style tags, such as jazz, electronic, etc.
                    example: Jazz
              title:
                allOf:
                  - type: string
                    description: Music title
                    example: Relaxing Piano
              negativeTags:
                allOf:
                  - type: string
                    description: >-
                      Excluded music styles, used to avoid specific style
                      elements in the replacement segment
                    example: Rock
              infillStartS:
                allOf:
                  - type: number
                    description: >-
                      Start time point for replacement (seconds), 2 decimal
                      places. Must be less than infillEndS
                    example: 10.5
                    minimum: 0
              infillEndS:
                allOf:
                  - type: number
                    description: >-
                      End time point for replacement (seconds), 2 decimal
                      places. Must be greater than infillStartS
                    example: 20.75
                    minimum: 0
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      Callback URL for task completion. The system will send a
                      POST request to this URL when replacement is complete,
                      containing task status and results.


                      - Your callback endpoint should be able to accept POST
                      requests containing JSON payloads with replacement results

                      - For detailed callback format and implementation guide,
                      see [Replace Music Section
                      Callbacks](./replace-section-callbacks)

                      - Alternatively, you can use the get music details
                      interface to poll task status
                    example: https://example.com/callback
            required: true
            requiredProperties:
              - taskId
              - audioId
              - prompt
              - tags
              - title
              - infillStartS
              - infillEndS
        examples:
          example:
            value:
              taskId: 2fac****9f72
              audioId: e231****-****-****-****-****8cadc7dc
              prompt: A calm and relaxing piano track.
              tags: Jazz
              title: Relaxing Piano
              negativeTags: Rock
              infillStartS: 10.5
              infillEndS: 20.75
              callBackUrl: https://example.com/callback
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
                      Response status code


                      - **200**: Success - Request processed successfully

                      - **401**: Unauthorized - Authentication credentials
                      missing or invalid

                      - **402**: Insufficient credits - Account does not have
                      enough credits to perform this operation

                      - **404**: Not found - Requested resource or endpoint does
                      not exist

                      - **409**: Conflict - WAV record already exists

                      - **422**: Validation error - Request parameters failed
                      validation checks

                      - **429**: Rate limit exceeded - Exceeded request limit
                      for this resource

                      - **451**: Unauthorized - Failed to retrieve image. Please
                      verify any access restrictions set by you or your service
                      provider.

                      - **455**: Service unavailable - System is currently
                      undergoing maintenance

                      - **500**: Server error - Unexpected error occurred while
                      processing request
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
                        description: >-
                          Task ID for tracking task status. You can use this ID
                          to query task details and results through the "Get
                          Music Details" interface.
                        example: 5c79****be8e
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