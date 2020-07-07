# coding=utf-8
class SentenceConstant:
    LABEL = "sentence"
    PRIMARY_PROPERTY_NAME = "sentence_name"


class FeatureConstant:
    LABEL = "characteristic"
    PRIMARY_PROPERTY_NAME = "characteristic_name"


class CodeConstant:
    LABEL = "code_element"
    QUALIFIED_NAME = "qualified_name"


class DomainConstant:
    LABEL = "domain term"
    PRIMARY_PROPERTY_NAME = "term_name"


Relation_Extra_Key = "extra_info_key"


class FunctionalityConstant:
    LABEL = "functionality"
    PRIMARY_PROPERTY_NAME = "functionality_name"


class RelationNameConstant:
    Interface_2_Feature = "corresponding characteristic"
    has_Feature_Relation = "has characteristic"
    has_Constraint_Relation = "has constraint"
    Category_Function_Feature_Relation = "has functionality characteristic"
    Antonyms_Feature_Relation = "antonyms"
    Synonyms_Feature_Relation = "synonyms"
    Sentence_2_API = "describe"
    Ontology_IS_A_Relation = "is a"
    Ontology_Derive_Relation = "part of"
    Ontology_Consist_Of_Relation = "consist of"
    Ontology_Parallel_Relation = "parallel"
    Feature_Def_Sentence = "characteristic explanation"
    Domain_Def_Sentence = "category explanation"
    API_REPRESENT = "represent"
    ALTERNATIVE_RELATION = "alternative to"
    has_Functionality_Relation = "has functionality"
    Functionality_Compare_Relation = "functionality compare"
    has_Behavior_Relation = "has behavior"
    API_Be_Contained = "API be contained"
    Abstract_Func_Relation = "abstract functionality"
    Abstract_Characteristic_Relation = "abstract characteristic"
    Functionality_Object_Relation = "has functionality object"
    Characterisitc_Object_Relation = "has characteristic object"
    Method_Derive_Relation = "method derive"


class NPEntityType:
    API = 1
    CategoryType = 2
    CharacteristicType = 3
    FunctionalityType = 4
    FunctionalityCompareType = 5
    BehaviorType = 6


class ALLKnowledgeFromType:
    FROM_Class_Name_Func = 1
    FROM_Method_Name_Func = 2
    FROM_Text_Func = 3

    FROM_Class_Name_Category = 4
    FROM_Method_Name_Category = 5
    FROM_Text_Category = 6

    FROM_TEXT_Category_Relation_Based_ON_HP = 6.1
    FROM_TEXT_Category_Relation_Based_ON_OpenIE = 6.2
    FROM_APIStructure_Category = 7
    FROM_Prefix_Suffix_Category = 8

    FROM_Class_Name_Characteristic = 9
    FROM_Method_Name_Characteristic = 10
    FROM_Text_Characteristic = 11
    FROM_Text_Characteristic_Open_IE = 11.1
    # 一般的基于规则的抽取，要求主语是API
    FROM_Text_Characteristic_Based_On_Rule_API_IS_subject = 11.2
    FROM_Text_Characteristic_Based_On_Rule_NLP = 11.3
    # 有些是对动词的修饰e.g. write efficiently
    FROM_Text_Characteristic_Based_On_Verb_Plus_Adverb = 11.4

    FROM_SynonymsAntonyms_Characteristic = 12

    FROM_Text_Functionality_Based_On_Verb_Noun = 13
    FROM_Text_Functionality_Based_On_Verb_Passive_Noun = 14
    FROM_Text_Functionality_Based_On_Nonfunctional_Verb = 15
    FROM_NAME_2_NAME = 16
    FROM_Abstract_Name = 17
    FROM_Antonyms_Dict = 18
    FROM_TEXT_2_NAME = 19
