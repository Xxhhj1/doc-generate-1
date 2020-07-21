from flask import Flask, request, jsonify
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument
from sekg.graph.exporter.graph_data import GraphData

from project.knowledge_service import KnowledgeService
from project.doc_service import DocService
from project.utils.path_util import PathUtil

app = Flask(__name__)
pro_name = "jabref"
data_dir = PathUtil.doc(pro_name=pro_name, version="v1.1")
graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.4")
graph_data: GraphData = GraphData.load(graph_data_path)
doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)
knowledge_service = KnowledgeService(doc_collection)
doc_service = DocService()


@app.route('/')
def hello():
    return 'success'


# search doc info according to method name
@app.route('/get_doc/', methods=["GET", "POST"])
def doc_info():
    if "qualified_name" not in request.json:
        return "qualified name need"
    qualified_name = request.json['qualified_name']
    node = graph_data.find_one_node_by_property(property_name="qualified_name", property_value=qualified_name)
    result = doc_service.get_doc_info(node['id'])
    return jsonify(result)


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


# return top5 key methods of specific class
@app.route('/key_methods/', methods=["POST", "GET"])
def key_methods():
    if "qualified_name" not in request.json:
        return "qualified_name need"
    qualified_name = request.json['qualified_name']
    methods_list = knowledge_service.get_key_methods(qualified_name)
    for i in range(len(methods_list)):
        methods_list[i] = methods_list[i][0]
    result = dict()
    result["key_methods"] = methods_list
    return jsonify(result)


if __name__ == '__main__':
    app.run()
