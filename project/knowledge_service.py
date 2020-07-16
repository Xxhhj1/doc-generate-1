from sekg.graph.exporter.graph_data import GraphData
from project.utils.path_util import PathUtil


class KnowledgeService:
    def __init__(self):
        graph_data_path = PathUtil.graph_data(pro_name="jabref", version="v1.1")
        self.graph_data = GraphData.load(graph_data_path)

    def get_api_characteristic(self, api_id):
        pass

    def get_api_functionality(self, api_id):
        pass

    def get_api_category(self, api_id):
        pass

    def get_api_id_by_name(self, name):
        node = self.graph_data.find_one_node_by_property(property_name=GraphData.DEFAULT_KEY_PROPERTY_QUALIFIED_NAME,
                                                         property_value=name)
        if node is not None:
            api_id = node['properties']['api_id']
        else:
            api_id = -1
        return api_id

    def get_knowledge(self, name):
        knowledge = dict()
        knowledge["message"] = ""
        api_id = self.get_api_id_by_name(name)
        if api_id == -1:
            knowledge["message"] = "can't find api by name"
            return knowledge
        knowledge["characteristic"] = self.get_api_characteristic(api_id)
        knowledge["functionality"] = self.get_api_functionality(api_id)
        knowledge["category"] = self.get_api_category(api_id)
        return knowledge
