from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, jsonify
from openai import ChatCompletion
import openai

es = Elasticsearch(hosts=["http://127.0.0.1:9200"])
print(f"Connected to ElasticSearch cluster `{es.info().body['cluster_name']}`")

MAX_SIZE = 15

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search")
def search_autocomplete():
    query = request.args["q"].lower()

    payload = {
        "multi_match" : {
            "query" : query,
            "operator": "and",
            "fields" : ["triệu_chứng", "dấu_hiệu", "biểu_hiện"]
        }  
    } 

    resp = es.search(index="medical", query=payload, size=MAX_SIZE, source=["tên_bệnh", "triệu_chứng", "dấu_hiệu", "biểu_hiện"], sort="_score:desc")
    return jsonify([result['_source']['tên_bệnh'] for result in resp['hits']['hits']])

@app.route("/chitietbenh/<slap>")
def details(slap):
    query = slap.lower()

    payload = {
        "query": {
            "match": {
                "tên_bệnh": query
            }
        }
    }

    resp = es.search(index="medical", body=payload, size=MAX_SIZE)

    results = [hit['_source'] for hit in resp['hits']['hits']]

    return render_template('details.html', slap=slap, results=results)

# Thiết lập khóa API của bạn
openai.api_key = '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'

@app.route("/send-message", methods=['POST'])
def send_message():
    request_data = request.json
    message = request_data['message']
    details = request_data['details']
    
    # Sử dụng thông tin từ details-container ở đây để cung cấp dữ liệu cho API trả lời câu hỏi
    
    response = openai.Completion.create(
        engine='gpt-3.5-turbo-instruct',
        prompt=message + '\n' + details,  # Kết hợp tin nhắn và thông tin từ details-container
        max_tokens=150
    )

    return jsonify({'answer': response.choices[0].text.strip()})

if __name__ == "__main__":
    app.run(debug=True)
