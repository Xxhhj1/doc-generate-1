from sekg.util.dependency_tree_util import DependencyTreeUtil

from data_model.simple_sentence import SimpleSentence
from model.rule_model.func.vb_np_extractor import VBNPStatementExtractor
from model.statement_extractor import StatementExtractor


class VBThanStatementExtractor(StatementExtractor):
    # AE1 VB ((ADP) NP)+ RBR than AE2 (COND)
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "vb_than"
        self.vb_np = VBNPStatementExtractor()

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
        if not self.is_rbr_than_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_A_verb_more(sent_doc, subject, predicate, doc_api_name)

    def is_rbr_than_template(self, sent_doc, subject, predicate):
        # 检查是不是类似faster than这种pattern
        has_than = False
        is_than_flag = False
        for than_token in sent_doc:
            if than_token.pos_ == 'ADV' and than_token.tag_ == 'RBR':
                is_than_flag = True
            if than_token.text == 'than':
                has_than = True
        if has_than and is_than_flag:
            return True
        return False

    def extract_for_A_verb_more(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        for token in sent_doc:
            if token.tag_ == 'RBR':
                if token.head.pos_ == "ADV":
                    filter_span = DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree(
                        sent_doc, token.head, predicate)
                    more_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, token.head)
                else:
                    filter_span = DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree(
                        sent_doc, token, predicate)
                    more_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, token)
                try:
                    if filter_span is None or filter_span.end_char == 0 or filter_span.text == "":
                        return statement_record_list
                except Exception as e:
                    print(e)
                    return statement_record_list
                sub_sub_sent = self.self_doc(filter_span.text)

                filter_relation_tuple_result = self.vb_np.extract_for_A_verb_NP(sub_sub_sent,
                                                                                DependencyTreeUtil.get_subject(
                                                                                    sub_sub_sent),
                                                                                DependencyTreeUtil.get_main_predicate(
                                                                                    sub_sub_sent),
                                                                                doc_api_name, allow_condition=True)
                statement_record_list.extend(filter_relation_tuple_result)
                compare_object = ''
                for noun_token in more_span:
                    if noun_token.tag_.startswith('NN') or noun_token.dep_ == 'pobj':
                        compare_object = noun_token.text
                        replace_text = filter_span.text.replace(subject.root.text, noun_token.text)
                        replaced_doc = self.nlp(replace_text)
                        replaced_doc = DependencyTreeUtil.merge_np_chunks(replaced_doc)
                        replaced_doc = DependencyTreeUtil.merge_np_of_np(replaced_doc)
                        noun_subject = DependencyTreeUtil.get_subject(replaced_doc)
                        predicate = DependencyTreeUtil.get_main_predicate(replaced_doc)

                        filter_object_relation_tuple_result = \
                            self.vb_np.extract_for_A_verb_NP(
                                replaced_doc, noun_subject, predicate, doc_api_name, allow_condition=True)
                        statement_record_list.extend(filter_object_relation_tuple_result)

        return statement_record_list
