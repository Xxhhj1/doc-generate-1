from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument
from sekg.graph.exporter.graph_data import GraphData
from sekg.graph.exporter.graph_data import NodeInfo
import json

field_name = 'dp_comment'
graph_data_location = './jabref.v1.graph'
dc_location = './jabref.1.dc'
dc_file = './jabref.v1.1.dc'
comment_json_file = './comment_机器学习生成版.json'
qualified_name_json_file = './qualified_name.json'
# 根据全限定名称去查找相应的node
key = 'qualified_name'

if __name__ == '__main__':
    # 加载文档集合
    doc_collection = MultiFieldDocumentCollection.load(dc_location)
    graph_data = GraphData.load(graph_data_location)

    # 处理json文件
    comment_list = []
    comment = open(comment_json_file, 'r').readlines()
    for line in comment:
        comment_list.append(json.loads(line))

    qualified_name_list = []
    name = open(qualified_name_json_file, 'r').readlines()
    for line in name:
        qualified_name_list.append(json.loads(line))
    for item in qualified_name_list:
        # 根据qualified_name找到node
        node = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=item[key])
        # 将注释加入dc
        doc_collection.add_field_to_doc(doc_id=node['properties']['api,id'], field_name=field_name,
                                        value=comment_list[item['mid'] - 1]['nl'])

    doc_collection.save(dc_file)
