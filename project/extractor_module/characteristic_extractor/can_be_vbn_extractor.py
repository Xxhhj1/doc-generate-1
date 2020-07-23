from sekg.util.dependency_tree_util import DependencyTreeUtil

from project.extractor_module.constant.constant import RelationNameConstant, ALLKnowledgeFromType, NPEntityType
from project.extractor_module.data_model.simple_sentence import SimpleSentence
from project.extractor_module.data_model.statement_record import StatementRecord
from project.extractor_module.statement_extractor import StatementExtractor


class CanBeVBNStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "can_be_vbn"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []

        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_can_be_vbn(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                          doc_api_name))

        return statement_record_list

    def extract_for_A_can_be_vbn(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_A_be_jj_np_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_A_could_be_xxx(sent_doc, subject, predicate, doc_api_name)

    def is_A_be_jj_np_template(self, sent_doc, subject, predicate):
        if predicate.pos_ == "VERB" and predicate.tag_ == "VBN":
            core_feature = DependencyTreeUtil.get_can_be_string(sent_doc, predicate)
            if core_feature is not None:
                return True
        return False

    def extract_for_A_could_be_xxx(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        core_feature = DependencyTreeUtil.get_can_be_string(sent_doc, predicate)
        if core_feature is None:
            return statement_record_list
        feature_span = DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree(sent_doc,
                                                                                                        subject.root,
                                                                                                        predicate)
        if feature_span is None or feature_span.end_char != 0 or feature_span.text == '':
            return statement_record_list

        neg = False
        for f in feature_span:
            if f.dep_ == "neg":
                neg = not neg
        condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, feature_span.root)
        feature_span_swap_text = DependencyTreeUtil.swap_condition_to_end(feature_span, predicate)
        span_two = feature_span_swap_text.split('$$')
        if len(span_two) > 1:
            second = span_two[1].replace(subject.text, '', 1).strip()
            feature_span_swap_text = span_two[0] + '' + second
        feature_span_swap_text.strip()
        extra_info = {
            "condition": condition_text,
            "core": core_feature,
            "leading_verb": predicate.lemma_,
            "neg": neg,
            "compare_subject": '',
            "compare_object": '',
        }

        info_from_set = set()
        info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))

        relation_data_tuple = StatementRecord(subject.text,
                                              RelationNameConstant.has_Feature_Relation,
                                              feature_span_swap_text,
                                              NPEntityType.CategoryType,
                                              NPEntityType.CharacteristicType,
                                              self.extractor_name, info_from_set, **extra_info)

        statement_record_list.append(relation_data_tuple)
        # feature_relation_tuple_result = self.get_feature_for_category(
        #     sent_doc, subject, predicate, doc_api_name)
        # statement_record_list.extend(feature_relation_tuple_result)
        return statement_record_list

    # def get_feature_for_category(self, sent_doc, subject, predicate, doc_api_name):
    #     """
    #     e.g. A is a File that can be modified.
    #     e.g. StringBuffer is a thread-safe, mutable char sequence.
    #     category entity -> file
    #     category entity -> char sequence
    #     抽取出来 A ->has feature ->can be modified.
    #     抽取出来 StringBuffer ->has feature ->thread-safe.
    #     抽取出来 StringBuffer ->has feature ->mutable.
    #     :param sent_doc:
    #     :param subject:
    #     :param predicate:
    #     :param category_entity:
    #     :return:
    #     """
    #     statement_record_list = []
    #     for token in sent_doc:
    #         if token.dep_ == "relcl":
    #             if token.head == subject.root:
    #                 text = subject.text
    #                 if text == sent_doc.text:
    #                     return statement_record_list
    #                 if 'that' in text or 'which' in text or 'who' in text:
    #                     text = re.sub(r'that | which | who', '', text)
    #                 attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
    #                 if attr_span:
    #                     change_object_span_text = text.replace(subject.root.text, attr_span.root.text)
    #                     object_doc_relations = self.statement_extractor_pipeline.extract_from_text(
    #                         change_object_span_text,
    #                         doc_api_name)
    #                     statement_record_list.extend(object_doc_relations)
    #
    #                 statement_record_list.extend(self.statement_extractor_pipeline.extract_from_text(text,
    #                                                                                                  doc_api_name,
    #                                                                                                  ))
    #                 return statement_record_list
    #             else:
    #                 attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
    #                 if attr_span is None:
    #                     return statement_record_list
    #                 else:
    #                     if token in attr_span:
    #                         text = attr_span.text
    #                         if text == sent_doc.text:
    #                             return statement_record_list
    #                         if 'that' in text or 'which' in text or 'who' in text:
    #                             text = re.sub(r'that | which | who', '', text)
    #                         change_subject_span_text = text.replace(token.head.text, subject.root.text)
    #                         attr_doc_relations = self.statement_extractor_pipeline.extract_from_text(
    #                             text,
    #                             doc_api_name, )
    #                         subject_doc_relations = self.statement_extractor_pipeline.extract_from_text(
    #                             change_subject_span_text, doc_api_name)
    #                         statement_record_list.extend(attr_doc_relations)
    #                         statement_record_list.extend(subject_doc_relations)
    #                         return statement_record_list
    #                     else:
    #                         return statement_record_list
    #     return statement_record_list
