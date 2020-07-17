from sekg.util.dependency_tree_util import DependencyTreeUtil

from data_model.simple_sentence import SimpleSentence
from model.rule_model.behavior.behavior_vb_np_extractor import BehaviorVBNPStatementExtractor
from model.rule_model.func.vb_np_extractor import VBNPStatementExtractor
from model.statement_extractor import StatementExtractor


class BehaviorJJOrNPVBGToStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "behavior_jj_or_np_vbg_to"
        self.vb_np = BehaviorVBNPStatementExtractor()

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_functionality(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                       doc_api_name))

        return statement_record_list

    def extract_functionality(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_vbg_to_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_verb(sent_doc, subject, predicate, doc_api_name)

    def is_vbg_to_template(self, sent_doc, subject, predicate):
        if sent_doc.text.find(" to ") < 0:
            return False
        if predicate.lemma_ == "be" and (predicate.pos_ == "VERB" or predicate.pos_ == "AUX"):
            for token in sent_doc:
                if token.lemma_ == "to" and token.head.tag_.lower().find("v") >= 0:
                    return True
        return False

    def extract_for_verb(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        for token in sent_doc:
            if token.lemma_ == "to" and token.head.tag_.lower().find(
                    "v") >= 0 and predicate.lemma_ == "be":
                sub_sent_doc = DependencyTreeUtil.get_subtree_span_from_functional_verb(sent_doc, token.head)
                neg = False
                for f in sub_sent_doc:
                    if f.dep_ == "neg":
                        neg = not neg
                not_str = 'not ' if neg else ''

                verb_text = token.head.lemma_
                if not str(subject.text).endswith("s"):
                    verb_text = self.inflect_engine.plural(verb_text)
                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, predicate)
                sub_sentence = subject.text + ' ' + not_str + verb_text + ' ' + sub_sent_doc.text + " " + condition_text
                if len(sub_sentence) >= len(sent_doc.text):
                    return []
                simple_sentence = SimpleSentence(doc_api_name, sent_doc, self.self_doc(sub_sentence))
                statement_record_list = self.vb_np.extract_from_simple_sentence(simple_sentence)
                return statement_record_list
        return statement_record_list
