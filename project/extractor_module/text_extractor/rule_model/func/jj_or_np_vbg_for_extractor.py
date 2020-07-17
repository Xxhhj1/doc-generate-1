from sekg.util.dependency_tree_util import DependencyTreeUtil

from data_model.simple_sentence import SimpleSentence
from model.rule_model.func.vb_np_extractor import VBNPStatementExtractor
from model.statement_extractor import StatementExtractor


class JJOrNPVBGForStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "jj_or_np_vbg_for"
        self.vb_np = VBNPStatementExtractor()

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []

        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_be_used_for(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                           doc_api_name))

        return statement_record_list

    def extract_for_A_be_used_for(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_vbg_for_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_verb(sent_doc, subject, predicate, doc_api_name)

    def is_vbg_for_template(self, sent_doc, subject, predicate):
        if sent_doc.text.find(" for ") < 0:
            return False
        if predicate.lemma_ == "be" and (predicate.pos_ == "VERB" or predicate.pos_ == "AUX"):
            return True
        return False

    def extract_for_verb(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        neg = False
        for f in sent_doc:
            if f.dep_ == "neg":
                neg = not neg

        for token in sent_doc:
            if token.head.lemma_ == "for" and token.dep_.find("comp") > 0:
                not_str = ' not ' if neg else ''
                sub_sent_doc = DependencyTreeUtil.get_subtree_span_from_functional_verb(sent_doc, token)
                if token.tag_.lower().find("v") < 0:
                    # reading 这种有时候会判断为NN
                    verb_text = self.lemmatizer.lemmatize(token.lemma_, 'v')
                else:
                    verb_text = token.lemma_
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
