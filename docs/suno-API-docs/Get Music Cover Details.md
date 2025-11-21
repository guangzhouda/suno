# Get Music Cover Details

> Get detailed information about music cover generation tasks.

## OpenAPI

````yaml suno-api/suno-api.json get /api/v1/suno/cover/record-info
paths:
  path: /api/v1/suno/cover/record-info
  method: get
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
      query:
        taskId:
          schema:
            - type: string
              required: true
              description: >-
                Unique identifier of the Cover generation task to retrieve. This
                is the taskId returned when creating the Cover generation task.
      header: {}
      cookie: {}
    body: {}
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

                      - **400**: Format error - Parameters are not in valid JSON
                      format

                      - **401**: Unauthorized - Authentication credentials
                      missing or invalid

                      - **402**: Insufficient credits - Account doesn't have
                      enough credits for this operation

                      - **404**: Not found - Requested resource or endpoint
                      doesn't exist

                      - **409**: Conflict - Cover record already exists

                      - **422**: Validation error - Request parameters failed
                      validation checks

                      - **429**: Rate limited - Request rate limit exceeded for
                      this resource

                      - **455**: Service unavailable - System currently
                      undergoing maintenance

                      - **500**: Server error - Unexpected error occurred while
                      processing request
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
                      parentTaskId:
                        type: string
                        description: Original music task ID
                        example: 73d6128b3523a0079df10da9471017c8
                      callbackUrl:
                        type: string
                        description: Callback URL
                        example: https://api.example.com/callback
                      completeTime:
                        type: string
                        format: date-time
                        description: Completion callback time
                        example: '2025-01-15T10:35:27.000Z'
                      response:
                        type: object
                        description: Completion callback result
                        properties:
                          images:
                            type: array
                            items:
                              type: string
                            description: Cover image URL array
                            example:
                              - >-
                                https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                              - >-
                                https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
                      successFlag:
                        type: integer
                        description: >-
                          Task status flag: 0-Pending, 1-Success, 2-Generating,
                          3-Generation failed
                        enum:
                          - 0
                          - 1
                          - 2
                          - 3
                        example: 1
                      createTime:
                        type: string
                        format: date-time
                        description: Creation time
                        example: '2025-01-15T10:33:01.000Z'
                      errorCode:
                        type: integer
                        format: int32
                        description: |-
                          Error code

                          - **200**: Success - Request processed successfully
                          - **500**: Internal error - Please try again later.
                        example: 200
                        enum:
                          - 200
                          - 500
                      errorMessage:
                        type: string
                        description: Error message
                        example: ''
        examples:
          example:
            value:
              code: 200
              msg: success
              data:
                taskId: 21aee3c3c2a01fa5e030b3799fa4dd56
                parentTaskId: 73d6128b3523a0079df10da9471017c8
                callbackUrl: https://api.example.com/callback
                completeTime: '2025-01-15T10:35:27.000Z'
                response:
                  images:
                    - >-
                      https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                    - >-
                      https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
                successFlag: 1
                createTime: '2025-01-15T10:33:01.000Z'
                errorCode: 200
                errorMessage: ''
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