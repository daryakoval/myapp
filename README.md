# Similar Words API Documentation

## Introduction

The "Similar Words API" is a small web service based on Flask that provides functionality to find words in the English dictionary that are similar to a given word. Two words are considered similar if one is a letter permutation of the other. For example, "stressed" and "desserts" are similar words.

The API uses a provided English dictionary file to perform the similarity checks. The service can handle a high rate of parallel requests efficiently and provides statistics about the program's usage.

## Setup and Running the Service

To run the "Similar Words API" service, follow the instructions below.

### Prerequisites

- Docker (if you want to run the application in a container).

### Running the service
1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

2. Build the Docker Image. You can build the Docker image using the provided Dockerfile.

```bash
docker build -t myapp .
```

3. Run the service with docker

```bash
docker run -p 8000:8000 myapp
```

The service will now be running and listening on port 8000.

## Endpoints

| **URL**         | **Method** | **Response**                                                        |
|-----------------|------------|---------------------------------------------------------------------|
| /api/v1/similar | GET        | Returns all words in the dictionary that similar to requested word. |
| /api/v1/stats   | GET        | Return general statistics about the program                         |


### GET /api/v1/similar?word=\<word\>

Returns all words in the dictionary that have the same permutation as the provided word. The word in the query is not returned.

#### Example
**Request URL:** `GET /api/v1/similar?word=apple`

**Response:**
```json
{
    "similar":["appel","pepla"]
}
```

### GET /api/v1/stats

Return general statistics about the program:
- Total number of words in the dictionary.
- Total number of requests (not including "stats" requests).
- Average time for request handling in nanoseconds (not including "stats" requests).

#### Example
**Request URL:** `GET /api/v1/stats`

**Response:**
```json
{
    "totalWords": 351075,
    "totalRequests": 9,
    "avgProcessingTimeNs": 45239
}
```

## Algorithm for Finding Similar Words - TODO

To find similar words efficiently, the service uses a hash map to group words with the same set of characters. For each incoming word, the service calculates its character frequency and checks if a word with the same character frequency exists in the hash map. If so, it adds the word to the list of similar words.

The time complexity of this algorithm is O(N * M), where N is the number of words in the dictionary, and M is the average word length. The space complexity is O(N) to store the hash map of words.

## Error Handling and Logging

The service logs all errors and relevant information to stdout/stderr. Error responses are returned with appropriate HTTP status codes and error messages in the response body.

## CPU and Memory Optimization - TODO

The algorithm used to find similar words is efficient in terms of CPU and memory usage. By using a hash map to group words with the same character frequency, the service reduces the need for exhaustive comparisons. Additionally, the service uses the Flask framework, which is lightweight and efficient for handling web requests.

## Parallel Requests - TODO

The service is designed to handle parallel requests efficiently. Since the process of finding similar words is not computationally intensive, multiple requests can be processed simultaneously without significant impact on performance.
