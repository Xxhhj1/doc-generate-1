from sekg.graph.exporter.graph_data import GraphData
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection

from project.utils.path_util import PathUtil


class GraphLoadUtil:

    @staticmethod
    def load_graph_data(is_jdk=True, version="v1"):
        if is_jdk:
            graph_data_path = PathUtil.jdk_graph_data(version)
        else:
            graph_data_path = PathUtil.android_graph_data(version)

        return GraphData.load(graph_data_path)

    @staticmethod
    def load_doc(project_name="android27", version="v1"):
        """
        project_name: jdk8 android27
        """
        document_collection_path = PathUtil.doc(pro_name=project_name, version=version)
        return MultiFieldDocumentCollection.load(document_collection_path)
