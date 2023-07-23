## TODO:
- unitests
- Fix cache memoize # @cache.memoize(timeout=60)
- change Entrypoint instead CMD (Dockerfile)
- Docker check \code is working directory 
- FROM python:3.11.4-bookworm
- Test with Hey / Apache Benchmark
- Update README
- learn all existing libraries and changes


## Running the server

1. Clone the repo.
2. Build the docker image using the following command: 
`docker build -t myapp .`
3. Run the container using the following command: `docker run -p 8000:8000 myapp`
