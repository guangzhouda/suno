# Boost Music Style

## OpenAPI

````yaml suno-api/suno-api.json post /api/v1/style/generate
paths:
  path: /api/v1/style/generate
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
              content:
                allOf:
                  - type: string
                    description: >-
                      Style description. Please describe in concise and clear
                      language the music style you expect to generate. Example:
                      'Pop, Mysterious'
                    example: Pop, Mysterious
            required: true
            requiredProperties:
              - content
        examples:
          example:
            value:
              content: Pop, Mysterious
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
                      param:
                        type: string
                        description: Request parameters
                      result:
                        type: string
                        description: The final generated music style text result.
                      creditsConsumed:
                        type: number
                        description: >-
                          Credits consumed, up to 5 digits, up to 2 decimal
                          places
                      creditsRemaining:
                        type: number
                        description: Credits remaining after this task
                      successFlag:
                        type: string
                        description: 'Execution result: 0-pending, 1-success, 2-failed'
                      errorCode:
                        type: number
                        description: Error code
                      errorMessage:
                        type: string
                        description: Error message
                      createTime:
                        type: string
                        description: Creation time
            refIdentifier: '#/components/schemas/ApiResponse'
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: <string>
                param: <string>
                result: <string>
                creditsConsumed: 123
                creditsRemaining: 123
                successFlag: <string>
                errorCode: 123
                errorMessage: <string>
                createTime: <string>
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