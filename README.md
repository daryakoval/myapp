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
git clone https://github.com/daryakoval/myapp.git
cd myapp
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
    "avgProcessingTimeNs": 97427,
    "totalRequests": 21000,
    "totalWords": 351075
}
```

## Algorithm for Finding Similar Words

To efficiently find similar words, the service utilizes a hash map to group words with identical character sets. 
When a requested word arrives, the service calculates its character frequency and checks if any words 
with the same frequency already exist in the hash map. 
If there is a match, the service retrieves the list of similar words, excluding the requested word, and returns the list.

For instance, consider a dictionary with the words ["appel", "pepla", "apple"]. The hash map representation would be:
```json
{
  "a1e1l1p2": ["appel", "pepla", "apple"]
}
```

When given the word "apple," the algorithm converts it to `a1e1l1p2` and queries the hash map to find similar words.

This algorithm has a time complexity of O(MlogM), where N is the number of words in the dictionary, and M is the average word length. The space complexity is O(N) to store the hash map of words. By employing this approach, the service can efficiently identify similar words and deliver the desired results.

