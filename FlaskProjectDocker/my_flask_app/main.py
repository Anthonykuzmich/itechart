from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch

app = Flask("movies_service")


@app.route("/api/movies/<movie_id>", methods=["GET"])
def movie_details(movie_id: str) -> str:
    total_docs = 1
    es = Elasticsearch()
    query_body = {"query": {"bool": {"must": {"match": {"id": movie_id}}}}}
    response = es.search(index="movies", body=query_body, size=total_docs)
    elastic_docs = response["hits"]["hits"]
    return jsonify(elastic_docs)


@app.route("/api/movies/", methods=["GET"], strict_slashes=False)
def movies_list():
    es = Elasticsearch()
    size = request.args.get("limit", default=50, type=int)
    page = request.args.get("page", default=1, type=int) - 1
    sort_title = request.args.get("sort", default="id", type=str)
    sort_order = request.args.get("sort_order", default="asc", type=str)
    response = es.search(
        index="movies",
        body={},
        size=size,
        from_=page * size,
        sort=f"_{sort_title}:{sort_order}",
    )
    elastic_docs = response["hits"]["hits"]
    return jsonify(elastic_docs)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
