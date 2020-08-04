from project.utils.path_util import PathUtil
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument
from sekg.graph.exporter.graph_data import GraphData
from sekg.graph.exporter.graph_data import NodeInfo
import json
from definitions import OUTPUT_DIR
from pathlib import Path

pro_name = 'jabref'
dc_file_location = PathUtil.doc(pro_name=pro_name, version='v1')
graph_data_file_location = PathUtil.graph_data(pro_name=pro_name, version='v1.8')
dc_file_destination = PathUtil.doc(pro_name=pro_name, version='v1.1')
comment_json_file = Path(OUTPUT_DIR) / "json" / "mid_2_dp_comment.json"
qualified_name_json_file = Path(OUTPUT_DIR) / "json" / "mid_2_qualified_name.json"

if __name__ == '__main__':
    doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(dc_file_location)
    graph_data: GraphData = GraphData.load(graph_data_file_location)

    comment_list = []
    comments = open(comment_json_file, 'r').readlines()
    for line in comments:
        comment_list.append(json.loads(line))

    qualified_name_list = []
    names = open(qualified_name_json_file, 'r').readlines()
    for line in names:
        qualified_name_list.append(json.loads(line))

    missing_count = 0
    # 根据qualified name找到graph data对应节点的api_id, 然后通过这个api_id找到doc_collection中对应的doc, 插入field和相应信息
    for item in qualified_name_list:
        qualified_name = item['qname']
        node: NodeInfo = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=qualified_name)
        if node is None:
            qualified_name_without_para = qualified_name[:qualified_name.find('(')]
            nodes = graph_data.find_nodes_by_property_value_starts_with(property_name='qualified_name', property_value_starter=qualified_name_without_para)
            if len(nodes) is not 0:
                node = nodes[0]
            if node is not None:
                doc_collection.add_field_to_doc(doc_id=node['id'], field_name='dp_comment', value=comment_list[item['mid'] - 1]['nl'])
    doc_collection.save(dc_file_destination)
