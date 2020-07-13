from nltk import WordNetLemmatizer
from sekg.constant.constant import CodeConstant
from sekg.text.extractor.domain_entity.relation_detection import RelationDetector, RelationType
from sekg.util.code import CodeElementNameUtil
from sekg.util.vocabulary_conversion.vocabulary_conversion import VocabularyConversion

import re

from project.extractor_module.base_structure_extractor import BaseStructureExtractor
from project.extractor_module.constant.constant import RelationNameConstant, NPEntityType, ALLKnowledgeFromType
from project.extractor_module.data_model.statement_record import StatementRecord


class CategoryStructureExtractor(BaseStructureExtractor):
    def __init__(self):
        super().__init__()
        self.extractor_name = "category_structure"
        self.api_id_2_statement = dict()
        # 所有的category名称，用于补充上下位关系
        self.category_entity_set = set()
        self.category_relation_tool = RelationDetector()
        # self.lemmatizer = WordNetLemmatizer()
        self.code_element_tool = CodeElementNameUtil()

    def extract_ontology_from_class_name(self):
        """
        从类名中抽取ontology entity
        :return:
        """
        print("from class name")
        for node_id, node_json in self.graph_data.graph.nodes(data=True):
            try:
                if "properties" in node_json and "api_type" in node_json["properties"] \
                        and (node_json["properties"][
                                 "api_type"] in self.type_of_class):
                    qualified_name = node_json['properties'][CodeConstant.QUALIFIED_NAME]
                    name = qualified_name.split('.')[-1]
                    # self.lemmatizer.lemmatize(name)
                    un_name = self.code_element_tool.uncamelize(name)
                    word_set = set(un_name.split(" "))
                    word_set.add(un_name)
                    relation_set = self.category_relation_tool.detect_relation_by_starfix(word_set)
                    ontology_set = self.extract_camle_name(qualified_name)
                    ontology_set.add(un_name)
                    self.category_entity_set.update(ontology_set)
                    info_from_set = set()
                    info_from_set.add((ALLKnowledgeFromType.FROM_Class_Name_Category, qualified_name,
                                       qualified_name))

                    for relation in relation_set:
                        if un_name.lower() != relation[0].lower():
                            continue
                        if relation[1] == RelationType.IS_A:
                            if not un_name.lower().endswith(relation[2].lower()):
                                continue
                        elif relation[1] == RelationType.PART_OF:
                            if not un_name.lower().startswith(relation[2].lower()):
                                continue
                        extra_info = {
                            "condition": "",
                            "core": relation[2],
                            "leading_verb": "",
                            "compare_subject": '',
                            "compare_object": '',
                        }
                        relation_data_tuple = StatementRecord(qualified_name,
                                                              relation[1],
                                                              relation[2],
                                                              NPEntityType.CategoryType,
                                                              NPEntityType.CategoryType,
                                                              self.extractor_name, info_from_set, **extra_info
                                                              )
                        if node_id not in self.api_id_2_statement:
                            self.api_id_2_statement[node_id] = set()
                        self.api_id_2_statement[node_id].add(relation_data_tuple)

            except Exception as e:
                print(e)

    def extract_category_from_API_structure(self):
        """
        从API 关系结构中抽取 is a 关系
        :return:
        """
        print("extract_category_from_API_structure")
        for node_id in self.graph_data.get_node_ids():
            relations = self.graph_data.get_all_out_relations(node_id)
            for relation in relations:
                try:
                    if 'implements' not in relation[1] and 'extends' not in relation[1]:
                        continue
                    re1 = self.graph_data.get_node_info_dict(relation[0])
                    re2 = self.graph_data.get_node_info_dict(relation[2])
                    if 'api_type' in re1['properties'] and 'api_type' in re2['properties']:
                        if (re1['properties']['api_type'] in self.type_of_class) and (
                                re2['properties']['api_type'] in self.type_of_class):
                            name1 = re1['properties']['qualified_name'].split('.')[-1]
                            name2 = re2['properties']['qualified_name'].split('.')[-1]
                            filter_ret = self.filter_not_noun_relation(
                                (name1, RelationNameConstant.Ontology_IS_A_Relation, name2))
                            if filter_ret is not None:
                                info_from_set = set()
                                info_text = re1['properties']['qualified_name'] + " " + str(relation[1]) + " " + \
                                            re2['properties'][
                                                'qualified_name']
                                info_from_set.add((ALLKnowledgeFromType.FROM_APIStructure_Category, info_text,
                                                   re1['properties']['qualified_name']))
                                extra_info = {
                                    "condition": "",
                                    "core": name2,
                                    "leading_verb": "",
                                    "compare_subject": '',
                                    "compare_object": '',
                                }
                                self.category_entity_set.add(name1)
                                self.category_entity_set.add(name2)

                                relation_data_tuple = StatementRecord(name1,
                                                                      RelationNameConstant.Ontology_IS_A_Relation,
                                                                      name2,
                                                                      NPEntityType.CategoryType,
                                                                      NPEntityType.CategoryType,
                                                                      self.extractor_name, info_from_set, **extra_info
                                                                      )
                                if node_id not in self.api_id_2_statement:
                                    self.api_id_2_statement[node_id] = set()
                                self.api_id_2_statement[node_id].add(relation_data_tuple)

                except Exception as e:
                    print(e)

    def filter_not_noun_relation(self, relation):
        r1 = relation[0]
        r2 = relation[2]
        sent1 = ''.join(self.uncamelize(r1))
        sent2 = ''.join(self.uncamelize(r2))
        if (VocabularyConversion.couldBeHigh_probability(sent1.split(' ')[-1], 'a', 0.5)) or \
                (VocabularyConversion.couldBeHigh_probability(sent2.split(' ')[-1], 'a', 0.5)):
            return None
        pa = re.compile(r'.*able$')
        if not VocabularyConversion.couldBeHigh_probability(sent1.split(' ')[-1], 'n',
                                                            0.5) and sent1 != 'Hashtable':
            if pa.match(sent1.split(' ')[-1]) is not None:
                return None
        if not VocabularyConversion.couldBeHigh_probability(sent2.split(' ')[-1], 'n',
                                                            0.5) and sent2 != 'Hashtable':
            if pa.match(sent2.split(' ')[-1]) is not None:
                return None
        return relation

    def extract_from_category(self):
        self.extract_ontology_from_class_name()
        self.extract_category_from_API_structure()

    def run(self, **config):
        print("running component %r" % (self.type()))
        self.extract_from_category()
        self.save_json(self.json_save_path)
