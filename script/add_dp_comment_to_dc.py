#-*-coding:utf-8-*-
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument
from sekg.graph.exporter.graph_data import GraphData
from sekg.graph.exporter.graph_data import NodeInfo
import json

field_name = 'dp_comment'
dc_file_location = './jabref.v1.dc'
graph_data_file_location = './jabref.v1.graph'
dc_file_destination = './jabref.v1.1.dc'
comment_json_file = './comments_机器学习生成版.json'
qualified_name_json_file = './qualified_name.json'
# 此处对应qualified_name.json中全限定名称对应的key name
key = 'qualified_name'

if __name__ == '__main__':
    doc_collection:MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(dc_file_location)
    graph_data:GraphData = GraphData.load(graph_data_file_location)

    comment_list = []
    comments = open(comment_json_file, 'r').readlines()
    for line in comments:
        comment_list.append(json.loads(line))

    qualified_name_list = []
    names = open(qualified_name_json_file, 'r').readlines()
    for line in names:
        qualified_name_list.append(json.loads(line))

    # 根据qualified name找到graph data对应节点的api_id, 然后通过这个api_id找到doc_collection中对应的doc, 插入field和相应信息
    for item in qualified_name_list:
        node:NodeInfo = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=item[key])
        doc_collection.add_field_to_doc(doc_id=node['properties']['api_id'], field_name=field_name, value=comment_list[item['mid']-1]['nl'])

    doc_collection.save(dc_file_destination)


    