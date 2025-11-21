# Generate Music Cover

> Create personalized cover images for generated music.

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/suno/cover/generate
paths:
  path: /api/v1/suno/cover/generate
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
                      Original music task ID, should be the taskId returned by
                      the music generation interface.
                    example: 73d6128b3523a0079df10da9471017c8
              callBackUrl:
                allOf:
                  - type: string
                    format: uri
                    description: >-
                      URL address for receiving Cover generation task completion
                      updates. This parameter is required for all Cover
                      generation requests.


                      - The system will send POST requests to this URL when
                      Cover generation is complete, including task status and
                      results

                      - Your callback endpoint should be able to accept JSON
                      payloads containing cover image URLs

                      - For detailed callback format and implementation guide,
                      see [Cover Generation Callbacks](./cover-suno-callbacks)

                      - Alternatively, you can use the Get Cover Details
                      interface to poll task status
                    example: https://api.example.com/callback
            required: true
            requiredProperties:
              - taskId
              - callBackUrl
        examples:
          example:
            value:
              taskId: 73d6128b3523a0079df10da9471017c8
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
                    format: int32
                    description: Status code
                    example: 200
                  - type: integer
                    enum:
                      - 200
                      - 400
                      - 401
                      - 402
                      - 404
                      - 409
                      - 422
                      - 429
                      - 455
                      - 500
                    description: >-
                      Response status code


                      - **200**: Success - Request processed successfully

                      - **400**: Validation error - Cover already generated for
                      this task

                      - **401**: Unauthorized - Authentication credentials
                      missing or invalid

                      - **402**: Insufficient credits - Account doesn't have
                      enough credits for this operation

                      - **404**: Not found - Requested resource or endpoint
                      doesn't exist

                      - **409**: Conflict - Cover record already exists

                      - **422**: Validation error - Request parameters failed
                      validation checks

                      - **429**: Rate limited - Your call frequency is too high.
                      Please try again later.

                      - **455**: Service unavailable - System currently
                      undergoing maintenance

                      - **500**: Server error - Unexpected error occurred while
                      processing request

                      Build failed - Cover image generation failed
              msg:
                allOf:
                  - type: string
                    description: Status message
                    example: success
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
                        example: 21aee3c3c2a01fa5e030b3799fa4dd56
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: 21aee3c3c2a01fa5e030b3799fa4dd56
        description: Success
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