from project.utils.path_util import PathUtil
from sekg.graph.exporter.graph_data import GraphData, NodeInfo
from project.classification_module import method_classification
from nltk.corpus import wordnet as wn
from project.classification_module.method_classification import split


if __name__ == '__main__':
    # 1. 得到图中所有方法节点 2. qualified_name传入classification中做判断
    pro_name = "jabref"
    graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.6")
    graph_data: GraphData = GraphData.load(graph_data_path)
    graph_data_output_path = PathUtil.graph_data(pro_name=pro_name, version='v1.7')
    methods_id: set = graph_data.get_node_ids_by_label("method")
    nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
    verbs = {x.name().split('.', 1)[0] for x in wn.all_synsets('v')}

    count = [0,0,0,0,0]
    for i in iter(methods_id):
        node: NodeInfo = graph_data.find_nodes_by_ids(i)[0]
        qualified_name = node['properties']['qualified_name']
        label = method_classification.basic_classification(qualified_name)
        if label is "undefined":
            first_word = split(camel_case=qualified_name)
            if first_word in verbs:
                label = "mutator"
            if first_word in nouns:
                label = "accessor"

        if label is "accessor":
            count[0] += 1
            graph_data.add_label_by_node_id(node_id=i, label='accessor method')
        elif label is "mutator":
            count[1] += 1
            graph_data.add_label_by_node_id(node_id=i, label='mutator method')
        elif label is "creational":
            count[2] += 1
            # print(qualified_name)
            graph_data.add_label_by_node_id(node_id=i, label='creational method')
        elif label is "constructor":
            count[3] += 1
            # print(qualified_name)
            graph_data.add_label_by_node_id(node_id=i, label='constructor method')
        else:
            # print(qualified_name)
            graph_data.add_label_by_node_id(node_id=i, label='undefined method')
            count[4] += 1

    print(count)
    print(sum(count))
    graph_data.save(graph_data_output_path)


