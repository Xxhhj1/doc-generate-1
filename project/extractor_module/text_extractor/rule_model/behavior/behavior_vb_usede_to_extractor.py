from sekg.util.dependency_tree_util import DependencyTreeUtil

from data_model.simple_sentence import SimpleSentence
from model.rule_model.behavior.behavior_vb_np_extractor import BehaviorVBNPStatementExtractor
from model.statement_extractor import StatementExtractor


class BehaviorVBUsedToStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "behavior_vb_used_to"
        self.vb_np = BehaviorVBNPStatementExtractor()

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_be_used_to_do(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                             doc_api_name))

        return statement_record_list

    def extract_for_A_be_used_to_do(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_nonfunctional_verb_to_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_nonfunctional_verb(sent_doc, subject, predicate, doc_api_name)

    def is_nonfunctional_verb_to_template(self, sent_doc, subject, predicate):
        # is used/designed/provided to
        if predicate.tag_ == 'VBN':
            for token in sent_doc:
                if (token.head == predicate and token.dep_ == 'xcomp' and token.tag_ == 'VB') or \
                        (
                                token.head.head == predicate and token.dep_ == 'pcomp' and token.tag_ == 'VBG' and token.head.text == 'for'):
                    return True
        return False

    def extract_for_nonfunctional_verb(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if predicate.tag_ == 'VBN':
            for token in sent_doc:
                # be ~ed to do, be ~ed for doing
                if (token.head == predicate and token.dep_ == 'xcomp' and token.tag_ == 'VB') or \
                        (
                                token.head.head == predicate and token.dep_ == 'pcomp' and token.tag_ == 'VBG' and token.head.text == 'for'):
                    neg = False
                    for f in sent_doc:
                        if f.dep_ == "neg":
                            neg = not neg
                    not_str = ' not ' if neg else ''
                    sub_sent_doc = DependencyTreeUtil.get_subtree_span_from_functional_verb(sent_doc, token)
                    verb_text = token.lemma_
                    if not str(subject.text).endswith("s"):
                        verb_text = self.inflect_engine.plural(verb_text)
                    sub_sentence = subject.text + ' ' + not_str + verb_text + ' ' + sub_sent_doc.text
                    if len(sub_sentence) >= len(sent_doc.text):
                        return []
                    simple_sentence = SimpleSentence(doc_api_name, sent_doc, self.self_doc(sub_sentence))
                    statement_record_list = self.vb_np.extract_from_simple_sentence(simple_sentence)
                    return statement_record_list

        return statement_record_list
