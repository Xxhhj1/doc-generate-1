from sekg.util.dependency_tree_util import DependencyTreeUtil
from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.statement_extractor import StatementExtractor


class BeJJThanStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "be_jj_than"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []

        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_jj_than(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                       doc_api_name))

        return statement_record_list

    def extract_for_A_jj_than(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_A_jj_than_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_A_is_more_xxx(sent_doc, subject, predicate, doc_api_name)

    def is_A_jj_than_template(self, sent_doc, subject, predicate):
        # HashMap is faster than HashSet.
        # Iteration over a HashMap is faster.
        # Iteration over a HashMap is more expensive.
        if predicate.lemma_ == "be" and (predicate.pos_ == "VERB" or predicate.pos_ == "AUX"):
            for right in predicate.rights:
                if right is None:
                    continue
                if right.tag_ == "JJR":
                    return True
        return False

    def extract_for_A_is_more_xxx(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
        if attr_span is None:
            return statement_record_list

        attr_spans = self.new_split_span_into_parallel(sent_doc, attr_span)
        for attr_span in attr_spans:
            if attr_span is None or attr_span.text == "":
                continue

            if attr_span.root.pos_ == "ADJ" or attr_span.root.pos_ == "ADV":
                feature_name = attr_span.text
                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, predicate)
                neg = False
                subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
                for f in subtree_span:
                    if f.dep_ == "neg":
                        neg = not neg

                extra_info = {
                    "condition": condition_text,
                    "core": attr_span.root.text,
                    "leading_verb": attr_span.root.head.lemma_,
                    "neg": neg,
                    "compare_subject": '',
                    "compare_object": '',
                }
                if condition_text is not None and condition_text != "":
                    feature_name = feature_name + " " + condition_text

                info_from_set = set()
                info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))

                relation_data_tuple = StatementRecord(subject.text,
                                                      RelationNameConstant.has_Feature_Relation,
                                                      feature_name,
                                                      NPEntityType.CategoryType,
                                                      NPEntityType.CharacteristicType,
                                                      self.extractor_name, info_from_set, **extra_info)
                statement_record_list.append(relation_data_tuple)

        return statement_record_list
