from sekg.text.extractor.domain_entity.word_util import WordUtil
from project.extractor_module.base_structure_extractor import BaseStructureExtractor
from project.extractor_module.constant.constant import *
from project.extractor_module.data_model.statement_record import StatementRecord


class CharacteristicStructureExtractor(BaseStructureExtractor):
    def __init__(self):
        super().__init__()
        self.extractor_name = "characteristic_structure"

    def split_method_name_into_words(self, method_name):
        """
            # 把方法名拆开成单词列表
        :param method_name:
        :return:
        """
        if method_name is not None and method_name != "":
            underline_method_name = self.code_name_tool.uncamelize(method_name)
            if underline_method_name is None:
                return None
            if '_' in underline_method_name:
                words = underline_method_name.split('_')
                return words
            elif " " in underline_method_name:
                return underline_method_name.split(" ")
            else:
                return [underline_method_name]

    def extract_feature_from_class_name(self):
        """
        # 从类名中抽取feature，和从接口中抽差不多，数据是document_data中的所有数据，将class的全限命名拆成单个的单词，然后判断是否是形容词或者后缀是否是“able”并且不再block_list中
        # 三元组存在于feature_list中，从class中得到的feature存在于entity_set中。
        :return:
        """
        block_set = {'table', 'jtable', 'on', 'out', 'go', 'home', 'still', 'sound', 'surface', 'no', 'color', 'midi',
                     "set", "model"}
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
                    api_name = node_json["properties"]["qualified_name"]
                    class_name = api_name.split('.')[-1]
                    class_word_list = self.split_method_name_into_words(class_name)
                    if class_word_list is None:
                        continue
                    for i in range(0, len(class_word_list)):
                        if (WordUtil.couldBeADJ(class_word_list[i]) and class_word_list[
                            i].lower() not in block_set) or (
                                class_word_list[i][-4:] == 'able' and class_word_list[i].lower() not in block_set):
                            info_from_set = set()
                            info_from_set.add(
                                (ALLKnowledgeFromType.FROM_Class_Name_Characteristic, api_name, api_name))
                            extra_info = {
                                "condition": "",
                                "core": class_word_list[i],
                                "leading_verb": "",
                                "compare_subject": '',
                                "compare_object": '',
                            }
                            # if class_word_list[i].lower().endswith(" table"):
                            #     continue
                            if class_word_list[i].lower() == "table":
                                continue
                            relation_data_tuple = StatementRecord(api_name,
                                                                  RelationNameConstant.has_Feature_Relation,
                                                                  class_word_list[i],
                                                                  NPEntityType.CategoryType,
                                                                  NPEntityType.CharacteristicType,
                                                                  self.extractor_name, info_from_set, **extra_info
                                                                  )
                            self.api_id_2_statement[node_id].add(relation_data_tuple)

            except Exception as e:
                print(e)

    def get_class_name_by_qualified_name(self, qualified_name):
        """
            # 从全限命名中得到类名，就是按“.”拆开然后选最后一个
        :param qualified_name:
        :return:
        """
        if qualified_name is not None:
            return qualified_name.split('.')[-1]
        return None

    def get_qualified_name(self, node_dict):
        if 'properties' in node_dict and 'qualified_name' in node_dict['properties']:
            return node_dict["properties"]["qualified_name"]
        return ""

    def extract_feature_from_code_skeleton(self):
        """
        从代码结构中抽取特征
            # 从接口的名字中抽取feature，实际上是这么做的，因为无法从document_data中判断哪些类是接口，从graph_data中拿出所有“implements”关系的三元组，
            # 三元组的第一部分就是具体的某个java类，最后一部分就是interface，这里得到的interface是全限命名，先根据全限命名得到类名，然后利用正则表达式把这种驼峰式命名的类名拆成单个的单词；
            # 判断类名中的单词是否存在形容词或者后缀是否为“able”，并且不再block_set中；block_set是看数据总结出的可能会判定成adj但实际并不是形容词的集合（后续可能要改成大小写敏感）；
            # 如果满足条件的话，就加到feature_list和entity_list中。feature_list是存的（java类，has characteristic，形容词性接口）三元组，
            # entity_list中存的是（接口全限命名，corresponding characteristic， 形容词性接口）。
            # entity_set存的是所有筛选出的形容词性接口

        :return:
        """
        block_set = {'table', "hashtable", "Hashtable", 'jtable', 'on', 'out', 'go', 'home', 'still', 'sound',
                     'surface', 'no', 'color', 'midi'}
        if self.graph_data is not None:
            graph_data_relations = self.graph_data.get_relations(start_id=None, relation_type='implements', end_id=None)
            for each in graph_data_relations:
                try:
                    api_entity = self.graph_data.get_node_info_dict(each[0])
                    api_name = self.get_qualified_name(api_entity)
                    interface = self.graph_data.get_node_info_dict(each[2])
                    if api_entity is not None and interface is not None:
                        interface_name = self.get_class_name_by_qualified_name(self.get_qualified_name(interface))
                        interface_word_list = self.split_method_name_into_words(interface_name)
                        if interface_word_list is None:
                            continue
                        for interface_word in interface_word_list:
                            interface_word = interface_word.lower()
                            if (WordUtil.couldBeADJ(interface_word) and interface_word.lower() not in block_set) or (
                                    interface_word[-4:] == 'able' and interface_word.lower() not in block_set):
                                info_from_set = set()
                                info_from_set.add(
                                    (ALLKnowledgeFromType.FROM_Class_Name_Characteristic, interface_name,
                                     interface_name))
                                extra_info = {
                                    "condition": "",
                                    "core": interface_word.lower(),
                                    "leading_verb": "",
                                    "compare_subject": '',
                                    "compare_object": '',
                                }
                                relation_data_tuple = StatementRecord(api_name,
                                                                      RelationNameConstant.has_Feature_Relation,
                                                                      interface_word.lower(),
                                                                      NPEntityType.CategoryType,
                                                                      NPEntityType.CharacteristicType,
                                                                      self.extractor_name, info_from_set, **extra_info
                                                                      )
                                self.api_id_2_statement[each[0]].add(relation_data_tuple)
                except Exception as e:
                    print(e)

    def extract_from_characteristic_name(self):
        self.extract_feature_from_class_name()
        self.extract_feature_from_code_skeleton()

    def run(self, **config):
        print("running component %r" % (self.type()))
        self.extract_from_characteristic_name()
   