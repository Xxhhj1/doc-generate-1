from sekg.constant.constant import DomainConstant

from constant.constant import ALLKnowledgeFromType, FeatureConstant, FunctionalityConstant


class KnowledgeTypeEntity(object):
    def __init__(self, main_name, knowledge_type=DomainConstant.LABEL_DOMAIN_TERM, **extra_info):
        self.main_name = main_name
        self.info_from_set = set()
        self.extra_info = extra_info
        self.knowledge_type = knowledge_type

    def add_extra_info(self, property_name, property_value):
        self.extra_info[property_name] = property_value

    def get_main_name(self):
        return self.main_name

    def add_info_from(self, extract_way, source_text, doc_api_name=None):
        self.info_from_set.add((extract_way, source_text, doc_api_name))

    def get_info_from_set(self):
        return self.info_from_set

    def get_extra_info(self):
        return self.extra_info

    def to_json(self):
        base = {
            "main_name": self.get_main_name(),
            "knowledge_type": self.knowledge_type,
            "info_from_set": list(self.get_info_from_set()),
        }
        for k, v in self.extra_info.items():
            base[k] = v
        return base

    def __repr__(self):
        return str(self.to_json())

    def __hash__(self):
        return hash(self.get_main_name())


class TupleAndKnowledgeTypeFactory:
    @staticmethod
    def create_category_from_text(category_name, source_text, doc_api_name,
                                  extract_way=ALLKnowledgeFromType.FROM_Text_Category, ):
        knowledge_type = KnowledgeTypeEntity(main_name=category_name, type=DomainConstant.LABEL_DOMAIN_TERM)
        knowledge_type.add_info_from(extract_way=extract_way, source_text=source_text, doc_api_name=doc_api_name)
        return knowledge_type

    @staticmethod
    def create_category_from_name(category_name, source_name, doc_api_name,
                                  extract_way=ALLKnowledgeFromType.FROM_Class_Name_Category,
                                  ):
        knowledge_type = KnowledgeTypeEntity(main_name=category_name, type=DomainConstant.LABEL_DOMAIN_TERM)

        knowledge_type.add_info_from(extract_way=extract_way, source_text=source_name, doc_api_name=doc_api_name)
        return knowledge_type

    @staticmethod
    def create_feature_from_text(feature_name, source_text, doc_api_name,
                                 extract_way=ALLKnowledgeFromType.FROM_Text_Characteristic,
                                 **extra_info
                                 ):
        knowledge_type = KnowledgeTypeEntity(main_name=feature_name, type=FeatureConstant.LABEL_FEATURE, **extra_info)

        knowledge_type.add_info_from(extract_way=extract_way, source_text=source_text, doc_api_name=doc_api_name)
        return knowledge_type

    @staticmethod
    def create_feature_from_name(feature_name, source_text, doc_api_name,
                                 extract_way=ALLKnowledgeFromType.FROM_Class_Name_Characteristic,
                                 **extra_info
                                 ):
        knowledge_type = KnowledgeTypeEntity(main_name=feature_name, type=FeatureConstant.LABEL_FEATURE, **extra_info)

        knowledge_type.add_info_from(extract_way=extract_way, source_text=source_text, doc_api_name=doc_api_name)
        return knowledge_type

    @staticmethod
    def create_functionality_from_text(functionality_name, source_text, doc_api_name,
                                       extract_way=ALLKnowledgeFromType.FROM_Text_Func,
                                       **extra_info
                                       ):
        knowledge_type = KnowledgeTypeEntity(main_name=functionality_name,
                                             type=FunctionalityConstant.LABEL_FUNCTIONALITY, **extra_info)

        knowledge_type.add_info_from(extract_way=extract_way, source_text=source_text, doc_api_name=doc_api_name)
        return knowledge_type

    @staticmethod
    def create_functionality_from_name(functionality_name, source_text, doc_api_name,
                                       extract_way=ALLKnowledgeFromType.FROM_Method_Name_Func,
                                       **extra_info
                                       ):
        knowledge_type = KnowledgeTypeEntity(main_name=functionality_name,
                                             type=FunctionalityConstant.LABEL_FUNCTIONALITY, **extra_info)

        knowledge_type.add_info_from(extract_way=extract_way, source_text=source_text, doc_api_name=doc_api_name)
        return knowledge_type

    @staticmethod
    def create_abstract_functionality(verb_name, from_detail_name):
        functionality_extra_info = {
            "condition": "",
            "leading_verb": verb_name,
            "neg": False,
            "action object": ""
        }
        knowledge_type = KnowledgeTypeEntity(main_name=verb_name,
                                             type=FunctionalityConstant.LABEL_FUNCTIONALITY, **functionality_extra_info)
        extract_way = ALLKnowledgeFromType.FROM_Abstract_Name

        knowledge_type.add_info_from(extract_way=extract_way, source_text=from_detail_name, doc_api_name="")
        return knowledge_type

    @staticmethod
    def create_abstract_characteristic(clean_core, from_detail_name):
        clean_core = str(clean_core).strip()
        from_detail_name = str(from_detail_name).strip()
        extra_info = {
            "condition": "",
            "core": clean_core,
            "neg": False,
            "leading_verb": "",
            "compare_subject": "",
            "compare_object": "",
        }
        knowledge_type = KnowledgeTypeEntity(main_name=clean_core,
                                             type=FeatureConstant.LABEL_FEATURE, **extra_info)
        extract_way = ALLKnowledgeFromType.FROM_Abstract_Name

        knowledge_type.add_info_from(extract_way=extract_way, source_text=from_detail_name, doc_api_name="")
        return knowledge_type
