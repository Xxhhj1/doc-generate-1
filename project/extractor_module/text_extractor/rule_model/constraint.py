from sekg.util.dependency_tree_util import DependencyTreeUtil

from constant.constant import NPEntityType, RelationNameConstant, ALLKnowledgeFromType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.statement_extractor import StatementExtractor


class ConstraintExtractor(StatementExtractor):
    # AE PV NP
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "constraint"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        if not simple_sentence.valid_check():
            return statement_record_list
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_functionaloty_for_A_verb_Noun_with_object(sent_doc, simple_sentence.get_subject(),
                                                                   simple_sentence.get_predicate(),
                                                                   doc_api_name))
        return statement_record_list

    def is_constrain_template(self, sent_doc, subject, predicate):
        # permission verb, e.g., allow/guarantee/prohibit/limit
        if (
                predicate.pos_ == 'VERB' or predicate.text in DependencyTreeUtil.verb_set) and \
                predicate.tag_ != 'VBN' and predicate.lemma_ != "be":
            return True
        return False

    def extract_functionaloty_for_A_verb_Noun_with_object(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_constrain_template(sent_doc, subject, predicate):
            return statement_record_list
        functionality_span = DependencyTreeUtil.get_subtree_span_from_token_by_index(sent_doc, predicate)
        if functionality_span is None or functionality_span.text == "":
            return statement_record_list
        functionality_filter_swap_text = DependencyTreeUtil.swap_condition_to_end(sent_doc, predicate)
        span_two = functionality_filter_swap_text.split('$$')
        if len(span_two) > 1:
            second = span_two[1].replace(subject.text, '', 1).strip()
            functionality_filter_swap_text = span_two[0] + '' + second
        functionality_name = str(functionality_filter_swap_text).strip()
        neg = False
        if "not " in functionality_span.text:
            neg = True
        condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, functionality_span.root)

        if predicate.lemma_.lower() in self.allow_like_word or predicate.lemma_.lower() in self.limit_like_word or predicate.lemma_.lower() in self.guarantee_like_word or predicate.lemma_.lower() in self.prohibit_like_word or predicate.lemma_.lower() in self.depend_on_like_word:
            verb = ''
            if predicate.lemma_.lower() in self.allow_like_word:
                verb = 'allow'
            if predicate.lemma_.lower() in self.limit_like_word:
                verb = 'limit'
            if predicate.lemma_.lower() in self.guarantee_like_word:
                verb = 'guarantee'
            if predicate.lemma_.lower() in self.prohibit_like_word:
                verb = 'prohibit'
            if predicate.lemma_.lower() in self.depend_on_like_word:
                verb = 'depend on'
            extra_info = {
                "condition": condition_text,
                "core": verb,
                "leading_verb": verb,
                "neg": neg,
                "compare_subject": '',
                "compare_object": '',
            }
            constraint_name = functionality_name.replace(predicate.text, verb)
            info_from_set = set()
            info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))
            relation_data_tuple = StatementRecord(subject.text,
                                                  RelationNameConstant.has_Constraint_Relation,
                                                  constraint_name,
                                                  NPEntityType.CategoryType,
                                                  NPEntityType.CharacteristicType,
                                                  self.extractor_name, info_from_set, **extra_info)
            statement_record_list.append(relation_data_tuple)

        return statement_record_list
