from project.utils.path_util import PathUtil
from sekg.graph.exporter.graph_data import GraphData, NodeInfo

# org.jabref.model.entry.BibEntry

pro_name = "jabref"
graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.7")
graph_data_output_path = PathUtil.graph_data(pro_name=pro_name, version='v1.8')
graph_data: GraphData = GraphData.load(graph_data_path)

def list_method_info(qualified_name: str):
    node: NodeInfo = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=qualified_name)
    methods: set = graph_data.get_all_in_relations(node['id'])
    kinds_of_method = ['accessor method', 'mutator method', 'creational method', 'constructor method', 'undefined method']
    method_info = [0,0,0,0,0]
    for method in methods:
        node: NodeInfo = graph_data.find_nodes_by_ids(method[0])[0];
        # print(node['properties']['qualified_name'])
        labels = node['labels']
        for index in range(len(kinds_of_method)):
            if kinds_of_method[index] in labels:
                method_info[index] += 1
                # print(kinds_of_method[index])
    return method_info


def class_classification(method_info: list):
    num_of_methods = sum(method_info)
    if num_of_methods is 0:
        return 'pool class'
    # accessor, mutator, creational, constructor,
    if method_info[0]+method_info[1]/num_of_methods > 0.8:
        return 'entity class'
    elif method_info[2]/num_of_methods > 0.5:
        return 'factory class'
    elif method_info[1] > method_info[0]:
        return 'utility class'
    elif num_of_methods < 5:
        return 'pool class'
    else:
        return 'undefined class'


if __name__ == '__main__':
    # list_methods_info("org.jabref.model.entry.BibEntry")
    # list_class_info()
    class_id: set = graph_data.get_node_ids_by_label("class")
    result_count = [0, 0, 0, 0, 0]
    for i in iter(class_id):
        node: NodeInfo = graph_data.find_nodes_by_ids(i)[0]
        method_info = list_method_info(node['properties']['qualified_name'])
        result = class_classification(method_info)
        if result == 'entity class':
            # print(node['properties']['qualified_name'])
            result_count[0] += 1
            graph_data.add_label_by_node_id(node_id=i, label='entity class')
        elif result == 'factory class':
            result_count[1] += 1
            graph_data.add_label_by_node_id(node_id=i, label='factory class')
        elif result == 'utility class':
            result_count[2] += 1
            graph_data.add_label_by_node_id(node_id=i, label='utility class')
        elif result == 'pool class':
            graph_data.add_label_by_node_id(node_id=i, label='pool class')
            result_count[3] += 1
        else:
            graph_data.add_label_by_node_id(node_id=i, label='undefined class')
            result_count[4] += 1
    print(result_count)
    graph_data.save(graph_data_output_path)