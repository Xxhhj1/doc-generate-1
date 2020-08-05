from project.utils.path_util import PathUtil
from sekg.graph.exporter.graph_data import GraphData, NodeInfo
from sekg.ir.doc.wrapper import MultiFieldDocument, MultiFieldDocumentCollection
import json
import definitions
from pathlib import Path

pro_name = 'jabref'
graph_data_path = PathUtil.graph_data(pro_name=pro_name, version='v1.8')
doc_collection_path = PathUtil.doc(pro_name=pro_name, version='v1.1')
doc_collection_save_path = PathUtil.doc(pro_name=pro_name, version='v1.2')
api_to_example_json_path = Path(definitions.ROOT_DIR) / "output" / "json" / "api_2_example_sorted.json"
mid_to_method_info_json_path = Path(definitions.ROOT_DIR) / "output" / "json" / "mid_2_method_info_without_comment.json"
graph_data: GraphData = GraphData.load(graph_data_path)
doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(doc_collection_path)


def find_doc(qualified_name):
    node: NodeInfo = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=qualified_name)
    if node is None:
        node: NodeInfo = graph_data.find_one_node_by_property_value_starts_with(property_name='qualified_name', property_value_starter=qualified_name)
    doc = None
    if node is not None:
        api_id = node['id']
        doc: MultiFieldDocument = doc_collection.get_by_id(api_id)
    return doc


if __name__ == '__main__':
    with open(api_to_example_json_path, 'r') as f:
        api_to_mid = json.load(f)
    f.close()

    methods_info = []
    methods = open(mid_to_method_info_json_path, 'r').readlines()
    for method in methods:
        methods_info.append(json.loads(method)['method'])

    for qualified_name in iter(api_to_mid):
        doc = find_doc(qualified_name)
        if doc is None:
            raise ValueError('doc of {} not found'.format(qualified_name))
        mid_list = api_to_mid[qualified_name]
        print(mid_list)
        sample_code_list = list()
        count = 0
        index = 0
        while count < 5 and index < len(mid_list):
            print('check mid: ' + str(mid_list[index]))
            method_info: str = methods_info[mid_list[index]-1]
            index += 1
            if method_info.find('{') != -1 and method_info.count(';') > 1:
                sample_code_list.append(method_info)
                count += 1

        doc.add_field(field_name='sample_code', field_document=sample_code_list)
        doc_collection.save(doc_collection_save_path)
