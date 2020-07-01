import random,json
from flask import Flask, request
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument

app = Flask(__name__)
data_dir = './data/jabref.v1.dc'

@app.route('/')
def hello():
    return 'success'

@app.route('/get_doc', methods=["POST"])
def get_doc():
    # post json data will be like this:
    # {"name":"method_name"}
    # send result data will be like this:
    # {"return_type":"success", "doc_info":{"full_html_description":"...", "full_description":"...", "sentence_description"="..."}}
    data = request.get_json()['name']
    return_data = {'return_type': 'false', 'doc_info':{'full_html_description':None, 'full_description':None, 'sentence_description':None}}
    if data.strip() == "":
        print('do not get post value')
    else:
        doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)
        for i in range(doc_collection.get_num()):
            doc: MultiFieldDocument = doc_collection.get_by_index(i)
            if doc.get_name() == data:
                print(i)
                return_data['return_type'] = 'true'
                return_data['doc_info']['full_html_description'] = doc.get_doc_text_by_field('full_html_description')
                return_data['doc_info']['full_description'] = doc.get_doc_text_by_field('full_description')
                return_data['doc_info']['sentence_description'] = doc.get_doc_text_by_field('sentence_description')
                break
    return json.dumps(return_data)





if __name__ == '__main__':
	app.run()



