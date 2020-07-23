from sekg.util.dependency_tree_util import DependencyTreeUtil
from project.extractor_module.constant.constant import RelationNameConstant, ALLKnowledgeFromType, NPEntityType
from project.extractor_module.data_model.simple_sentence import SimpleSentence
from project.extractor_module.data_model.statement_record import StatementRecord

from project.extractor_module.statement_extractor import StatementExtractor

class BeJJNPStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "be_jj_np"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []

        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_be_jj_np(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                        doc_api_name))

        return statement_record_list

    def extract_for_A_be_jj_np(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_A_be_jj_np_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_A_is_xxx(sent_doc, subject, predicate, doc_api_name)

    def is_A_be_jj_np_template(self, sent_doc, subject, predicate):
        if predicate.lemma_ == "be" and (predicate.pos_ == "VERB" or predicate.pos_ == "AUX"):
            return True
        return False

    def extract_for_A_is_xxx(self, sent_doc, subject, predicate, doc_api_name):
        # AE be [a/an] JJ+ NP (COND)
        statement_record_list = []

        attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
        neg = False
        subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
        for f in subtree_span:
            if f.dep_ == "neg":
                neg = not neg
        if attr_span is None:
            return statement_record_list
        attr_spans = self.new_split_span_into_parallel(sent_doc, attr_span)
        for i, attr_span in enumerate(attr_spans):
            if attr_span is None or attr_span.text == "":
                continue
            try:
                if attr_span.root.pos_ == "NOUN" or attr_span.root.pos_ == 'PROPN':
                    noun_phase_doc = self.nlp(attr_span.text)
                    noun_phase, feature_list = DependencyTreeUtil.split_large_noun_phase_span_to_adj_and_np(
                        span=noun_phase_doc)
                    info_from_set = set()
                    info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))

                    for feature in feature_list:
                        extra_info = {
                            "condition": "",
                            "core": feature,
                            "leading_verb": attr_span.root.head.lemma_,
                            "compare_subject": '',
                            "compare_object": '',
                            "neg": neg,
                        }

                        info_from_set = set()
                        info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))

                        relation_data_tuple = StatementRecord(subject.text,
                                                              RelationNameConstant.has_Feature_Relation,
                                                              feature,
                                                              NPEntityType.CategoryType,
                                                              NPEntityType.CharacteristicType,
                                                              self.extractor_name, info_from_set, **extra_info)
                        statement_record_list.append(relation_data_tuple)

            except Exception as e:
                print(e)
        return statement_record_list
