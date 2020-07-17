from sekg.constant.constant import CodeConstant
from project.extractor_module.structure_extractor.base_structure_extractor import BaseStructureExtractor
from project.extractor_module.constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from project.extractor_module.data_model.statement_record import StatementRecord


class FuncNameExtractor(BaseStructureExtractor):
    def __init__(self):
        super().__init__()
        self.invalid_name = {"string"}
        self.extractor_name = "func_name"

    def find_functionality_in_class_qualified_name(self, api_qualified_name: str):
        """
        从类的全限定名中抽取动词关系
        :param api_qualified_name:
        :return:
        """
        relation_list = []
        simple_name = self.code_name_tool.simplify(api_qualified_name)
        term_set = set()
        name_list = self.code_name_tool.uncamelize_by_stemming(simple_name).split(" ")
        last_word = name_list[-1]
        if len(name_list) >= 2:
            end_name = " ".join(name_list[0:-1])
        else:
            end_name = ""
        verb, flag = self.vocabulary_conversion_tool.noun_2_verb(last_word)
        if verb is None:
            return term_set, relation_list
        lemma_verb = self.lemmatizer.lemmatize(verb.lower(), "v")
        if last_word.lower() != lemma_verb:
            relation_list.append((api_qualified_name, "operation_" + lemma_verb, end_name.lower()))
        return term_set, relation_list

    def extract_from_class_name(self):
        """
        根据规则从类名称里面抽取动词关系元组 (class_name,f_v,NP,[(C,class_name)])
        :return:
        """
        if self.graph_data is None:
            print("load graph data error")
        counter = 0
        for node_id, node_json in self.graph_data.graph.nodes(data=True):
            if node_id not in self.api_id_2_statement:
                self.api_id_2_statement[node_id] = set()
            try:
                if counter % 100 == 0:
                    print(counter)
                if "properties" in node_json and 'api_type' in node_json["properties"] \
                        and (node_json["properties"]["api_type"] in self.type_of_class):

                    counter += 1
                    qualified_name = node_json['properties'][CodeConstant.QUALIFIED_NAME]
                    terms, identifier_relation_list = self.find_functionality_in_class_qualified_name(qualified_name)

                    for identifier_relation in identifier_relation_list:
                        info_from_set = set()
                        info_from_set.add((ALLKnowledgeFromType.FROM_Class_Name_Func, qualified_name, qualified_name))
                        if identifier_relation[1].find("operation_") < 0:
                            continue
                        verb = identifier_relation[1].replace("operation_", "")
                        if verb in self.invalid_name:
                            continue
                        func_entity_name = verb + " " + identifier_relation[2]
                        functionality_extra_info = {
                            "condition": "",
                            "leading_verb": verb,
                            "neg": False,
                            "action object": identifier_relation[2]
                        }
                        relation_data_tuple = StatementRecord(qualified_name,
                                                              RelationNameConstant.has_Functionality_Relation,
                                                              func_entity_name,
                                                              NPEntityType.CategoryType,
                                                              NPEntityType.FunctionalityType,
                                                              self.extractor_name, info_from_set,
                                                              **functionality_extra_info)
                        self.api_id_2_statement[node_id].add(relation_data_tuple)

            except Exception as e:
                print(e)

    def extract_from_method_name(self):
        """
        根据规则从类名称里面抽取动词关系元组 (method_name,f_v,NP,[(M,method_name)])
        :return:
        """
        if self.graph_data is None:
            print("load graph data error")
        counter = 0
        for node_id, node_json in self.graph_data.graph.nodes(data=True):
            if node_id not in self.api_id_2_statement:
                self.api_id_2_statement[node_id] = set()
            try:
                if counter % 100 == 0:
                    print(counter)
                if "labels" in node_json and "method" in node_json["labels"]:
                    if 'properties' in node_json and 'qualified_name' in node_json['properties']:
                        counter += 1
                        qualified_name = node_json['properties'][CodeConstant.QUALIFIED_NAME]
                        terms, operations, relations, identifier_relation_list = \
                            self.identifier_extractor.extract_from_method_name(
                                qualified_name, mark_for_identifier_in_relation=qualified_name)
                        for identifier_relation in identifier_relation_list:
                            info_from_set = set()
                            if identifier_relation[1].find("operation_") < 0:
                                continue
                            verb = identifier_relation[1].replace("operation_", "")
                            if verb in self.invalid_name:
                                continue
                            func_entity_name = verb + " " + identifier_relation[2]
                            info_from_set.add(
                                (ALLKnowledgeFromType.FROM_Method_Name_Func, qualified_name, qualified_name))
                            functionality_extra_info = {
                                "condition": "",
                                "leading_verb": verb,
                                "neg": False,
                                "action object": identifier_relation[2]
                            }
                            relation_data_tuple = StatementRecord(qualified_name,
                                                                  RelationNameConstant.has_Functionality_Relation,
                                                                  func_entity_name,
                                                                  NPEntityType.CategoryType,
                                                                  NPEntityType.FunctionalityType,
                                                                  self.extractor_name, info_from_set,
                                                                  **functionality_extra_info)
                            self.api_id_2_statement[node_id].add(relation_data_tuple)
            except Exception as e:
                print(e)

    def extract_from_func_name(self):
        self.extract_from_class_name()
        self.extract_from_method_name()

    def run(self, **config):
        print("running component %r" % (self.type()))
        self.extract_from_func_name()
        self.save_json(self.json_save_path)

