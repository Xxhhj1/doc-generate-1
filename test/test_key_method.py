from project.utils.path_util import PathUtil

from sekg.graph.exporter.graph_data import GraphData, NodeInfo
from project.knowledge_service import KnowledgeService

if __name__ == '__main__':
    pro_name = "jabref"
    graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.4")
    knowledge_service = KnowledgeService()
    qualified_name = "org.jabref.model.entry.BibEntry"
    graph_data: GraphData = GraphData.load(graph_data_path)

    methods = knowledge_service.api_contains_method(qualified_name)
    methods_list = []
    for i in range(len(methods)):
        method_name = methods[i]["name"]
        method_value = graph_data.find_nodes_by_ids(knowledge_service.get_api_id_by_name(method_name))[0]["properties"]["pr_value"]
        methods_list.append((method_name, method_value))

    methods_list.sort(key=lambda x:x[1], reverse=True)
    for i in range(10):
        print(methods_list[i])