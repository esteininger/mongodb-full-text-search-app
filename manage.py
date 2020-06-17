from flask import Flask, render_template, request, jsonify
import os
import pymongo
import ssl

full_url = "mongodb://127.0.0.1:27017/clintrials"

app = Flask(__name__)

# connection obj
conn = pymongo.MongoClient(full_url, ssl_cert_reqs=ssl.CERT_NONE)
# collection
collection = conn['clintrials']['clinical_studies']

# endpoint
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', default=None, type=str)
    path = request.args.get('f', default='brief_title', type=str)

    agg_pipeline = [
        {
            '$search': {
                'term': {
                    'query': query,
                    'path': path,
                    'fuzzy': {
                        'maxEdits': 2,
                        'prefixLength': 0
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'brief_title': 1,
                'source': 1,
                'score': {
                    '$meta': 'searchScore'
                }
            }
        }, {
            '$limit': 15
        }
    ]
    results = list(collection.aggregate(agg_pipeline))
    # json_result = json_util.dumps({'docs': docs}, json_options=RELAXED_JSON_OPTIONS)
    return jsonify(results)

# page
@app.route('/')
def index():
    return render_template("index.html")

# {
#   $search: {
#     <operator>: {
#       <specification(s)>
#     }
#   }
# }


if __name__ == '__main__':
    app.run(host="localhost", port=5010, debug=True)
