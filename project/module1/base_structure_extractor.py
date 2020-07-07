from nltk import WordNetLemmatizer
from sekg.constant.code import CodeEntityCategory
from sekg.pipeline.component.base import Component
from sekg.text.extractor.domain_entity.identifier_util import IdentifierInfoExtractor
from sekg.text.spacy_pipeline.pipeline import PipeLineFactory
from sekg.util.code import CodeElementNameUtil
from sekg.util.vocabulary_conversion.vocabulary_conversion import VocabularyConversion
import re

from project.module1.constant.constant import FunctionalityConstant, FeatureConstant, DomainConstant, \
    RelationNameConstant
from project.module1.data_model.statement_record import StatementRecord


class BaseStructureExtractor(Component):
    def __init__(self, ):
        super().__init__()
        self.code_name_tool = CodeElementNameUtil()
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
        self.lemmatizer = WordNetLemmatizer()
        self.vocabulary_conversion_tool = VocabularyConversion()
        self.identifier_extractor = IdentifierInfoExtractor()
        self.nlp = PipeLineFactory.full_pipeline()
        self.camel_cache = {}
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
        # 保存结果的地方
        self.api_id_2_statement = dict()
        self.graph_out_path = None

    def uncamelize_classname(self, classname):
        """

        :param classname:
        :return:
        """
        if not classname:
            return None
        if re.match('^[0-9A-Z]+$', classname):
            return classname
        sub = re.sub(r'([A-Z0-9]+)([A-Z]+[a-z0-9])', r'\1 \2', classname).strip()
        sub = re.sub(r'_', " ", sub)
        sub = re.sub(r'([A-Z]+[0-9])([A-Z][a-z0-9]+)', r'\1 \2', sub)
        sub = re.sub(r'([A-Z]*[0-9]?[A-Z]+)', r' \1', sub)
        sub = re.sub(r'\s+', " ", sub).strip()
        return sub

    def extract_camle_name(self, name):
        split_name = name.split('.')
        last_name = split_name[len(split_name) - 1]
        sent = ''.join(self.uncamelize_classname(last_name))
        doc = self.nlp(sent)
        ret = list()
        ret.append(sent)
        for word in doc:
            if word.tag_ == 'NNP' or word.tag_ == 'NN':
                ret.append(str(word.text).strip())
        return set(ret)

    def get_part_of_method_name(self, qualified_name):
        return qualified_name.split("(")[0]

    def uncamelize(self, camel_case):
        """
        uncamelize the ontology named in camel format. eg. ArrayList->Array List
        :param camel_case:
        :return:
        """
        if camel_case in self.camel_cache:
            return self.camel_cache[camel_case]
        sub = self.code_name_tool.uncamelize_by_stemming(camel_case)
        self.camel_cache[camel_case] = sub
        return sub

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

    def after_run(self, **config):
        super().after_run(**config)
        print("after running component %r" % (self.type()))
        counter = 0
        for i, api_id in enumerate(self.api_id_2_statement):
            statement_list = self.api_id_2_statement[api_id]
            if i % 1000 == 0:
                print(i)
            counter += len(statement_list)
            for statement in statement_list:
                statement_node_id = self.create_statement_entity(statement)
                self.add_relations(api_id, statement.r_name, statement_node_id)
        self.graph_data.save(self.graph_out_path)
        print("counter" + str(counter))

    def set_save_path(self, p):
        self.graph_out_path = p
