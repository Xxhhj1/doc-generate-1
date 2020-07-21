from flask import Flask, request, jsonify
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument
from sekg.graph.exporter.graph_data import GraphData

from project.knowledge_service import KnowledgeService
from project.utils.path_util import PathUtil

app = Flask(__name__)
pro_name = "jabref"
data_dir = PathUtil.doc(pro_name=pro_name, version="v1")
graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1")
graph_data: GraphData = GraphData.load(graph_data_path)
doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)
knowledge_service = KnowledgeService()


@app.route('/')
def hello():
    return 'success'


# search doc info according to method name
@app.route('/get_doc', methods=["POST"])
def get_doc():
    name = request.get_json()['name']
    return_data = {'return_type': 'false',
                   'doc_info': {'full_html_description': None, 'full_description': None, 'sentence_description': None}}
    if name.strip() == "":
        print('do not receive method name')
    else:
        node = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=name)
        if node is None:
            print('can not find method which name is ' + name)
        else:
            api_id = node["id"]
            print('success to find, api_id is %d' % api_id)
            doc: MultiFieldDocument = doc_collection.get_by_id(api_id)
            return_data['return_type'] = 'true'
            return_data['doc_info']['full_html_description'] = doc.get_doc_text_by_field('full_html_description')
            return_data['doc_info']['full_description'] = doc.get_doc_text_by_field('full_description')
            return_data['doc_info']['sentence_description'] = doc.get_doc_text_by_field('sentence_description')
    return jsonify(return_data)


@app.route('/api_knowledge/', methods=["POST", "GET"])
def api_knowledge():
    if "qualified_name" not in request.json:
        return "qualified_name need"
    qualified_name = request.json['qualified_name']
    result = knowledge_service.get_knowledge(qualified_name)
    return jsonify(result)


@app.route('/api_structure/', methods=["POST", "GET"])
def api_structure():
    if "qualified_name" not in request.json:
        return "qualified_name need"
    qualified_name = request.json['qualified_name']
    result = knowledge_service.api_base_structure(qualified_name)
    return jsonify(result)


if __name__ == '__main__':
    app.run()
