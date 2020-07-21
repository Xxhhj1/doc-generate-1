import networkx as nx

from sekg.graph.exporter.graph_data import GraphData, NodeInfo
from project.utils.path_util import PathUtil

if __name__ == '__main__':
    pro_name = "jabref"
    graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.3")
    output_path = PathUtil.graph_data(pro_name=pro_name, version="v1.4")

    graph_data: GraphData = GraphData.load(graph_data_path)
    nx_graph = nx.Graph(graph_data.graph)
    result = nx.pagerank(nx_graph)
    # todo: result是一个字典格式{node_id: pr_value},将其插入graph相应节点的node['properties']['pr_value']中
    for i in range(41167):
        node: NodeInfo = graph_data.find_nodes_by_ids(i+1)[0]
        node["properties"]["pr_value"] = result[i+1]
    graph_data.save(output_path)

