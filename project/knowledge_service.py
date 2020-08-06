from sekg.constant.code import CodeEntityRelationCategory
from sekg.constant.constant import WikiDataConstance
from sekg.graph.exporter.graph_data import GraphData
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument

from project.extractor_module.constant.constant import RelationNameConstant, FeatureConstant, DomainConstant, \
    FunctionalityConstant, SentenceConstant, CodeConstant
from project.utils.path_util import PathUtil
import re


class KnowledgeService:
    def __init__(self, doc_collection):
        graph_data_path = PathUtil.graph_data(pro_name="jabref", version="v1.8")
        self.graph_data = GraphData.load(graph_data_path)
        self.doc_collection = doc_collection

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
        method_list = self.parse_res_list(res_list)
        for m in method_list:
            m["declare"] = self.get_declare_from_method_name(m["name"])
            m["parameters"] = self.method_parameter(m["id"])
            m["return_value"] = self.method_return_value(m["id"])
            m["doc_info"] = self.get_method_doc_info(m["id"])
        method_list.sort(key=lambda x: x['declare'])
        # 排除构造方法
        count = 0
        for m in method_list:
            if m['declare'][0] < 'a':
                count += 1
            else:
                break;
        method_list = method_list[count:]
        return method_list

    def get_desc_from_api_id(self, api_id):
        doc: MultiFieldDocument = self.doc_collection.get_by_id(api_id)
        if doc is None:
            return ""
        full_description = doc.get_doc_text_by_field('full_description')
        if full_description == "":
            short_description = doc.get_doc_text_by_field('short_description')
            return short_description
        return full_description

    def get_method_doc_info(self, method_id):
        res = dict()
        doc: MultiFieldDocument = self.doc_collection.get_by_id(method_id)
        full_description = doc.get_doc_text_by_field('full_description')
        # res["full_description"] = full_description
        # res["comment"] = doc.get_doc_text_by_field('dp_comment')
        dp_comment = doc.get_doc_text_by_field('dp_comment')
        # 正则处理去掉多余字符
        dp_comment = re.sub(r"</?(.+?)>", "", dp_comment)
        dp_comment = dp_comment.lstrip().rstrip()
        if full_description != "" and full_description is not None:
            res['comment'] = full_description
        elif dp_comment != "" and dp_comment is not None:
            res['comment'] = 'DL Auto Generate: ' + dp_comment
        else:
            res['comment'] = ''
        return res

    def method_parameter(self, method_id):
        res_list = []
        res_list.extend(self.api_relation_search(method_id, CodeEntityRelationCategory.category_code_to_str_map[
            CodeEntityRelationCategory.RELATION_CATEGORY_HAS_PARAMETER]))
        for r in res_list:
            if r[1]['properties']['short_description'] == "":
                r[1]['properties']['short_description'] = self.get_desc_from_api_id(r[1]["id"])
            r[1]['properties']['description'] = r[1]['properties']['short_description']
            r[1]['labels'] = list(r[1]['labels'])
        return res_list

    def method_return_value(self, method_id):
        res_list = []
        res_list.extend(self.api_relation_search(method_id, CodeEntityRelationCategory.category_code_to_str_map[
            CodeEntityRelationCategory.RELATION_CATEGORY_HAS_RETURN_VALUE]))
        if len(res_list) > 0:
            r = res_list[0]
            if r[1]['properties']['description'] == "":
                r[1]['properties']['description'] = self.get_desc_from_api_id(r[1]["id"])
            r[1]["labels"] = list(r[1]["labels"])
            return res_list[0]
        return dict()

    def get_api_father_class(self, api_id):
        # API 的父类是什么
        res_list = []
        res_list.extend(self.api_relation_search(api_id, CodeEntityRelationCategory.category_code_to_str_map[
            CodeEntityRelationCategory.RELATION_CATEGORY_EXTENDS]))
        return self.parse_res_list(res_list)

    def get_api_implement_class(self, api_id):
        # API implements了哪些
        res_list = []
        res_list.extend(self.api_relation_search(api_id, CodeEntityRelationCategory.category_code_to_str_map[
            CodeEntityRelationCategory.RELATION_CATEGORY_IMPLEMENTS]))
        return self.parse_res_list(res_list)

    def get_api_terminologies(self, api_name):
        """
        API的术语
        :return []:
        """
        api_id = self.get_api_id_by_name(api_name)
        if api_id == -1:
            return []
        candidates = self.graph_data.get_relations(start_id=api_id, relation_type="has terminology",
                                                   end_id=None)
        node_list = []
        for (s, r, e) in candidates:
            end_node = self.graph_data.get_node_info_dict(e)
            node_list.append((end_node['properties']['terminology_name'], end_node['properties']["score"]))
        sorted(node_list, key=lambda x: x[1], reverse=True)
        return node_list

    def parse_res_list(self, res_list):
        parse_res = []
        for relation_type, node in res_list:
            t = {"id": node["id"], "relation": relation_type, "name": self.get_name_of_node_by_different_label(node)}
            if "properties" in node and 'full_description' in node["properties"]:
                t["full_description"] = node["properties"]["full_description"]
            parse_res.append(t)
        return parse_res

    def get_declare_from_method_name(self, method_name: str):
        if method_name is None or method_name == "":
            return ""
        font = method_name[0:method_name.find("(")]
        font = font.split(".")[-1]
        font += method_name[method_name.find("("):]
        return font

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
            end_node = self.graph_data.get_node_info_dict(e)
            node_list.append((r, end_node))
        return node_list

    def api_by_relation_search(self, api_id, relation_type):
        node_list = []
        candidates = self.graph_data.get_relations(start_id=None, relation_type=relation_type,
                                                   end_id=api_id)
        for (s, r, e) in candidates:
            start_node = self.graph_data.get_node_info_dict(s)
            node_list.append((r, start_node))
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
        # knowledge["functionality"] = self.get_api_functionality(api_id)
        knowledge["category"] = self.get_api_category(api_id)
        return knowledge

    def api_contains_method(self, api_name):
        api_id = self.get_api_id_by_name(api_name)
        return self.get_api_methods(api_id)

    def api_father_class(self, api_id):
        res = dict()
        father_class_list = self.get_api_father_class(api_id)
        if len(father_class_list) > 0:
            return father_class_list[0]
        else:
            res = {"relation": CodeEntityRelationCategory.category_code_to_str_map[
                CodeEntityRelationCategory.RELATION_CATEGORY_EXTENDS], "name": "java.lang.Object"}
            return res

    def api_implement_class(self, api_id):
        get_api_implement_class_list = self.get_api_implement_class(api_id)
        return get_api_implement_class_list

    def api_field(self, api_id):
        res_list = []
        res_list.extend(self.api_relation_search(api_id, CodeEntityRelationCategory.category_code_to_str_map[
            CodeEntityRelationCategory.RELATION_CATEGORY_HAS_FIELD]))
        for r in res_list:
            r[1]['labels'] = list(r[1]['labels'])

        return res_list

    def api_base_structure(self, api_name):
        # 继承树
        api_id = self.get_api_id_by_name(api_name)
        res = dict()
        res["methods"] = self.get_api_methods(api_id)
        res["extends"] = self.api_father_class(api_id)
        res["implements"] = self.api_implement_class(api_id)
        res["fields"] = self.api_field(api_id)
        return res

    # 返回类下面5个最关键方法
    def get_key_methods(self, api_name):
        methods = self.api_contains_method(api_name)
        methods_list = []
        for i in range(len(methods)):
            method_name = methods[i]["name"]
            method_value = \
                self.graph_data.find_nodes_by_ids(self.get_api_id_by_name(method_name))[0]["properties"]["pr_value"]
            methods_list.append((method_name, method_value))

        methods_list.sort(key=lambda x: x[1], reverse=True)
        return methods_list[:5]

    # 返回该类的构造方法信息
    def get_constructor(self, api_name):
        api_id: int = self.get_api_id_by_name(name=api_name)
        res = dict()
        all_methods = self.get_api_methods(api_id=api_id)
        count = 0
        for method in all_methods:
            if method['declare'][0] < 'a':
                count += 1
            else:
                break
        constructor_list = all_methods[:count]
        res['number_of_constructor'] = count
        res['constructor_detail'] = constructor_list
        return res


if __name__ == '__main__':
    pro_name = "jabref"
    data_dir = PathUtil.doc(pro_name=pro_name, version="v1.2")
    doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)

    knowledge_service = KnowledgeService(doc_collection)
    # knowledge_service.get_api_terminologies("org.jabref.logic.importer.fileformat.EndnoteImporter.A_PATTERN")
    t = knowledge_service.api_base_structure("org.jabref.benchmarks.Benchmarks")
    print(t)
    # t = knowledge_service.api_base_structure("org.jabref.gui.entryeditor.FieldsEditorTab")
    # print(t)

    t = knowledge_service.get_knowledge("org.jabref.gui.actions.OldDatabaseCommandWrapper")
    t = knowledge_service.get_knowledge("org.jabref.model.metadata.ContentSelectors")
    print(t)

    api_id = knowledge_service.get_api_id_by_name("org.jabref.model.metadata.event.MetaDataChangedEvent")
    t = knowledge_service.get_api_methods(api_id)
    print(t)
    api_id = knowledge_service.get_api_id_by_name(
        "org.jabref.gui.documentviewer.PageDimension.FixedHeightPageDimension")

    t = knowledge_service.api_father_class(api_id)
    print(t)
    api_id = knowledge_service.get_api_id_by_name("org.jabref.logic.bst.VM.MacroFunction")
    t = knowledge_service.api_implement_class(api_id)
    print(t)
    api_id = knowledge_service.get_api_id_by_name("org.jabref.gui.cleanup.CleanupAction")
    t = knowledge_service.api_field(api_id)
    print(t)

    for i in knowledge_service.get_constructor("org.jabref.model.entry.BibEntry")['constructor_detail']:
        print(i['declare'])
