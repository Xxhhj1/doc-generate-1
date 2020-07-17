from sekg.util.dependency_tree_util import DependencyTreeUtil
from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.statement_extractor import StatementExtractor


class VB_RBR_Than_Characteristic_StatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "vb_rbr_than_characteristic"

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
                if filter_span is None or filter_span.end_char != 0 or filter_span.text == '':
                    return statement_record_list
                compare_object = ''
                for noun_token in more_span:
                    if noun_token.tag_.startswith('NN') or noun_token.dep_ == 'pobj':
                        compare_object = noun_token.text
                        replace_text = filter_span.text.replace(subject.root.text, noun_token.text)
                        replaced_doc = self.self_doc(replace_text)
                        predicate = DependencyTreeUtil.get_main_predicate(replaced_doc)

                neg = False
                for f in filter_span:
                    if f.dep_ == "neg":
                        neg = not neg
                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, filter_span.root)
                extra_info = {
                    "condition": condition_text,
                    "core": token.text,
                    "leading_verb": predicate.lemma_,
                    "neg": neg,
                    "compare_subject": subject.root.text,
                    "compare_object": compare_object
                }
                feature_name = sent_doc.text
                info_from_set = set()
                info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))
                relation_data_tuple = StatementRecord(subject.text,
                                                      RelationNameConstant.has_Feature_Relation,
                                                      feature_name,
                                                      NPEntityType.CategoryType,
                                                      NPEntityType.CharacteristicType,
                                                      self.extractor_name, info_from_set, **extra_info)
                statement_record_list.append(relation_data_tuple)
                if compare_object != '':
                    info_from_set = set()
                    info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))
                    relation_data_tuple = StatementRecord(compare_object,
                                                          RelationNameConstant.has_Feature_Relation,
                                                          feature_name,
                                                          NPEntityType.CategoryType,
                                                          NPEntityType.CharacteristicType,
                                                          self.extractor_name, info_from_set, **extra_info)
                    statement_record_list.append(relation_data_tuple)

        return statement_record_list
