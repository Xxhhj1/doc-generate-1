from project.utils.path_util import PathUtil

from sekg.graph.exporter.graph_data import GraphData, NodeInfo
from project.knowledge_service import KnowledgeService

if __name__ == '__main__':
    pro_name = "jabref"
    graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.4")
    knowledge_service = KnowledgeService()
    qualified_name = "org.jabref.model.entry.BibEntry"
    graph_data: GraphData = GraphData.load(graph_data_path)

    result = KnowledgeService().get_key_methods(qualified_name)
    print(result)