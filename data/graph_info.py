from sekg.graph.exporter.graph_data import GraphData

graph_data: GraphData = GraphData.load('jabref.v1.graph')
print(graph_data.print_graph_info())