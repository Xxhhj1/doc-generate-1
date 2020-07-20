from sekg.constant.code import CodeEntityRelationCategory
from sekg.constant.constant import WikiDataConstance
from sekg.graph.exporter.graph_data import GraphData

from project.extractor_module.constant.constant import RelationNameConstant, FeatureConstant, DomainConstant, \
    FunctionalityConstant, SentenceConstant, CodeConstant
from project.utils.path_util import PathUtil


class KnowledgeService:
    def __init__(self):
        graph_data_path = PathUtil.graph_data(pro_name="jabref", version="v1.3")
        self.graph_data = GraphData.load(graph_data_path)

    def get_api_characteristic(self, api_id):
        res_list = []
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.has_Feature_Relation))
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.has_Constraint_Relation))
        return self.parse_res_list(res_list)

    def get_api_functionality(self, api_id):
        res_list = []
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.has_Functionality_Relation))
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.Functionality_Compare_Relation))
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.has_Behavior_Relation))
        return self.parse_res_list(res_list)

    def get_api_category(self, api_id):
        res_list = []
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.Ontology_IS_A_Relation))
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.Ontology_Derive_Relation))
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.Ontology_Consist_Of_Relation))
        res_list.extend(self.api_relation_search(api_id, RelationNameConstant.Ontology_Parallel_Relation))
        return self.parse_res_list(res_list)

    def get_api_methods(self, api_id):
        res_list = []
        res_list.extend(self.api_by_relation_search(api_id, CodeEntityRelationCategory.category_code_to_str_map[
            CodeEntityRelationCategory.RELATION_CATEGORY_BELONG_TO]))
        return self.parse_res_list(res_list)

    def parse_res_list(self, res_list):
        parse_res = []
        for relation_type, node in res_list:
            t = {"relation": relation_type, "name": self.get_name_of_node_by_different_label(node)}
            if "properties" in node and 'full_description' in node["properties"]:
                t["full_description"] = node["properties"]["full_description"]
            parse_res.append(t)
        return parse_res

    def get_name_of_node_by_different_label(self, node):
        """
        根据node的label类型，返回它的名称
        :param node:
        :return:
        """
        labels = node["labels"]
        if FeatureConstant.LABEL in labels:
            return node["properties"][FeatureConstant.PRIMARY_PROPERTY_NAME]
        if DomainConstant.LABEL in labels:
            return node["properties"][DomainConstant.PRIMARY_PROPERTY_NAME]
        if FunctionalityConstant.LABEL in labels:
            return node["properties"][FunctionalityConstant.PRIMARY_PROPERTY_NAME]
        if WikiDataConstance.LABEL_WIKIDATA in labels:
            if 'labels_en' in node["properties"]:
                return node["properties"]['labels_en']
            return node["properties"][WikiDataConstance.NAME]
        if SentenceConstant.LABEL in labels:
            return node["properties"][SentenceConstant.PRIMARY_PROPERTY_NAME]
        else:
            if CodeConstant.QUALIFIED_NAME in node["properties"]:
                return node["properties"][CodeConstant.QUALIFIED_NAME]
            else:
                return ""

    def api_relation_search(self, api_id, relation_type):
        node_list = []
        candidates = self.graph_data.get_relations(start_id=api_id, relation_type=relation_type,
                                                   end_id=None)
        for (s, r, e) in candidates:
            ontology_node = self.graph_data.get_node_info_dict(e)
            node_list.append((r, ontology_node))
        return node_list

    def api_by_relation_search(self, api_id, relation_type):
        node_list = []
        candidates = self.graph_data.get_relations(start_id=None, relation_type=relation_type,
                                                   end_id=api_id)
        for (s, r, e) in candidates:
            ontology_node = self.graph_data.get_node_info_dict(s)
            node_list.append((r, ontology_node))
        return node_list

    def get_api_id_by_name(self, name):
        node = self.graph_data.find_one_node_by_property(property_name=GraphData.DEFAULT_KEY_PROPERTY_QUALIFIED_NAME,
                                                         property_value=name)
        if node is not None:
            api_id = node["id"]
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

    def api_contains_method(self, api_name):
        api_id = self.get_api_id_by_name(api_name)
        return self.get_api_methods(api_id)


if __name__ == '__main__':
    knowledge_service = KnowledgeService()
    # t = knowledge_service.get_knowledge("org.jabref.model.metadata.ContentSelectors")
    t = knowledge_service.api_contains_method("org.jabref.model.metadata.event.MetaDataChangedEvent")
    # t = knowledge_service.get_knowledge("org.jabref.model.metadata.event.MetaDataChangedEvent")
    print(t)
