from pathlib import Path
import time

from sekg.constant.code import CodeEntityCategory
from sekg.constant.constant import CodeConstant
from sekg.graph.exporter.graph_data import GraphData
from sekg.util.code import CodeElementNameUtil
from definitions import OUTPUT_DIR
from project.extractor_module.constant.constant import RelationNameConstant, FeatureConstant, FunctionalityConstant, \
    DomainConstant
from project.extractor_module.data_model.statement_record import StatementRecord
from project.utils.graph_load_util import GraphLoadUtil
from project.utils.path_util import PathUtil
from project.utils.tool import Tool


class APIDiffGraphBuilder():
    """
    构建包含知识的API图谱
    """

    def __init__(self, input_graph_version):
        self.save_expand_res_path = str(Path(OUTPUT_DIR) / "prefix_suffix_relations.pickle")
        self.api_id_2_record_text_path = str(Path(OUTPUT_DIR) / "api_id_2_record.pickle")
        self.api_id_2_record_text = Tool.load_pickle(self.api_id_2_record_text_path)
        graph_data_path = PathUtil.graph_data(pro_name="jabref", version=input_graph_version)
        self.graph_data = GraphData.load(graph_data_path)
        self.func_relation_set = {
            RelationNameConstant.has_Functionality_Relation,
            RelationNameConstant.Functionality_Compare_Relation,
            RelationNameConstant.has_Behavior_Relation,
        }
        self.concept_classification = {
            RelationNameConstant.Ontology_IS_A_Relation,
        }
        self.membership = {
            RelationNameConstant.Ontology_Derive_Relation,
        }
        self.characteristic = {
            RelationNameConstant.has_Feature_Relation,
            RelationNameConstant.has_Constraint_Relation,
        }
        self.category_name_2_id = dict()
        self.type_of_class = {
            CodeEntityCategory.CATEGORY_CLASS,
            CodeEntityCategory.CATEGORY_INTERFACE,
            CodeEntityCategory.CATEGORY_EXCEPTION_CLASS,
            CodeEntityCategory.CATEGORY_ERROR_CLASS,
            CodeEntityCategory.CATEGORY_ENUM_CLASS,
            CodeEntityCategory.CATEGORY_ANNOTATION_CLASS
        }
        self.type_of_method = {
            CodeEntityCategory.CATEGORY_METHOD,
            CodeEntityCategory.CATEGORY_CONSTRUCT_METHOD,
            CodeEntityCategory.CATEGORY_BASE_OVERRIDE_METHOD,
        }
        self.CODE_NAME_UTIL = CodeElementNameUtil()

    def build_simple_graph(self):
        """
        只包含API和从API文档、结构抽取的图
        API -> relation -> statement
        """
        print("self.api_id_2_record_text:" + str(len(self.api_id_2_record_text)))
        self.graph_data.create_index_on_property(CodeConstant.QUALIFIED_NAME, "alias", DomainConstant
                                                 .PRIMARY_PROPERTY_NAME, FeatureConstant.PRIMARY_PROPERTY_NAME,
                                                 FunctionalityConstant.PRIMARY_PROPERTY_NAME,
                                                 )

        for i, api_id in enumerate(self.api_id_2_record_text):
            statement_list = self.api_id_2_record_text[api_id]
            if i % 1000 == 0:
                print(i)
            for statement in statement_list:
                statement_node_id = self.create_statement_entity(statement)
                self.add_relations(api_id, statement.r_name, statement_node_id)

    def add_relations(self, start_id, relation_str, end_id):
        """
        添加图中的关系
        @param start_id: 
        @param end_id: 
        @param relation_str: 
        @return: 
        """
        try:
            self.graph_data.add_relation(start_id, relation_str, end_id)
        except Exception as e:
            print(e)

    def get_record_entity_type_by_relation(self, relation: str):
        """
        @param relation:
        @return:
        """
        if relation in self.func_relation_set:
            return FunctionalityConstant
        if relation in self.concept_classification:
            return DomainConstant
        if relation in self.membership:
            return DomainConstant
        if relation in self.characteristic:
            return FeatureConstant

    def save_graph(self, path):
        self.graph_data.save(path)

    def create_category_node(self, name):
        label_info = {"entity"}
        type_class = DomainConstant
        label_info.add(str(type_class.LABEL))
        node_properties = {
            type_class.PRIMARY_PROPERTY_NAME: name
        }
        graph_id = self.graph_data.add_node(label_info, node_properties,
                                            primary_property_name=type_class.PRIMARY_PROPERTY_NAME)
        return graph_id

    def create_statement_entity(self, statement: StatementRecord):
        label_info = {"entity"}
        type_class = self.get_record_entity_type_by_relation(statement.r_name)
        label_info.add(str(type_class.LABEL))
        label_info.add(str("statement"))
        node_properties = {
            type_class.PRIMARY_PROPERTY_NAME: statement.e_name,
        }
        for extra_info_key in statement.extra_info:
            node_properties[extra_info_key] = statement.extra_info[extra_info_key]
        node_properties["which_extractor"] = statement.which_extractor
        node_properties["e_type"] = statement.e_type
        node_properties["s_name"] = statement.s_name
        node_properties["r_name"] = statement.r_name
        graph_id = self.graph_data.add_node(label_info, node_properties,
                                            primary_property_name=type_class.PRIMARY_PROPERTY_NAME)
        return graph_id


if __name__ == '__main__':
    start_time = time.asctime(time.localtime(time.time()))
    print(start_time)
    api_diff_graph_builder = APIDiffGraphBuilder(input_graph_version="v1.4")
    api_diff_graph_builder.build_simple_graph()
    api_diff_graph_builder.graph_data.save(PathUtil.graph_data(pro_name="jabref", version="v1.5"))
    end_time = time.asctime(time.localtime(time.time()))
    print(end_time)
