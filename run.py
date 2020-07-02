import random, json
import definitions
from flask import Flask, request
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument
from sekg.graph.exporter.graph_data import GraphData, NodeInfo

app = Flask(__name__)
data_dir = definitions.ROOT_DIR + "/data/jabref.v1.dc"
graph_dir = definitions.ROOT_DIR + "/data/jabref.v1.graph"


@app.route('/')
def hello():
    return 'success'


# search doc info according to method name
@app.route('/get_doc', methods=["POST"])
def get_doc():
    # post json data will be like this:
    # {"name":"method_name"}
    # send result data will be like this:
    # {"return_type":"success", "doc_info":{"full_html_description":"...", "full_description":"...", "sentence_description"="..."}}
    name = request.get_json()['name']
    return_data = {'return_type': 'false',
                   'doc_info': {'full_html_description': None, 'full_description': None, 'sentence_description': None}}
    if name.strip() == "":
        print('do not receive method name')
    else:
        doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)
        graph_data: GraphData = GraphData.load(graph_dir)
        node: NodeInfo = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=name)
        if node is None:
            print('can not find method which name is ' + name)
        else:
            api_id = node['properties']['api_id']
            print('success to find, api_id is %d' % api_id)
            doc: MultiFieldDocument = doc_collection.get_by_id(api_id)
            return_data['return_type'] = 'true'
            return_data['doc_info']['full_html_description'] = doc.get_doc_text_by_field('full_html_description')
            return_data['doc_info']['full_description'] = doc.get_doc_text_by_field('full_description')
            return_data['doc_info']['sentence_description'] = doc.get_doc_text_by_field('sentence_description')
    return json.dumps(return_data)


if __name__ == '__main__':
    app.run()
