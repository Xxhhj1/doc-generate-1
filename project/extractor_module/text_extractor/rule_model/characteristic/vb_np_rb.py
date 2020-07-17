from sekg.util.dependency_tree_util import DependencyTreeUtil
from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.statement_extractor import StatementExtractor


class VBNPRBStatementExtractor(StatementExtractor):
    # AE VB ((ADP) NP)+ RB (COND)
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "vb_rb"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []

        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.get_feature_for_functionality(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                               doc_api_name))

        return statement_record_list

    def get_feature_for_functionality(self, sent_doc, subject, predicate, doc_api_name):
        """
        某个功能有什么特征
        """
        # buffering character
        statement_record_list = []
        feature_name = ''
        for i, token in enumerate(sent_doc):
            if token.pos_ == 'ADV' and token.tag_ != 'WRB' and token.lemma_.lower() not in self.stop_feature and token.head == predicate:
                feature_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj_by_index(sent_doc, token, i)
                if feature_span is None:
                    return statement_record_list, feature_name
                feature_name = feature_span.text
                neg = False
                for f in feature_span:
                    if f.dep_ == "neg":
                        neg = not neg
                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, feature_span.root)
                extra_info = {
                    "condition": condition_text,
                    "core": feature_span.text,
                    "leading_verb": predicate.lemma_,
                    "neg": neg,
                    "compare_subject": '',
                    "compare_object": '',
                }
                info_from_set = set()
                info_from_set.add((ALLKnowledgeFromType.FROM_Text_Characteristic, sent_doc.text, doc_api_name))
                start_name = " ".join(sent_doc.text.replace(feature_name, "", 1).split())

                relation_data_tuple = StatementRecord(start_name,
                                                      RelationNameConstant.has_Feature_Relation,
                                                      feature_name,
                                                      NPEntityType.FunctionalityType,
                                                      NPEntityType.CharacteristicType,
                                                      self.extractor_name, info_from_set, **extra_info)
                statement_record_list.append(relation_data_tuple)

            if token.dep_ == 'advcl' and token.head == predicate:
                ifflag = False
                if token is None:
                    continue
                for sub_token in token.lefts:
                    if sub_token.lemma_.lower() in self.mark_filter_words:
                        ifflag = True
                if ifflag:
                    continue
                feature_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj_by_index(sent_doc, token, i)
                if feature_span is None:
                    return statement_record_list, feature_name
                if token.left_edge.text in self.stop_feature:
                    return statement_record_list, feature_name
                if token.left_edge.text == 'except' and token.left_edge.dep_ == 'mark':
                    clause_flag = False
                    clause = []
                    for span_token in feature_span:
                        if span_token.dep_.startswith('nsubj'):
                            clause_flag = True
                        if span_token.dep_ != 'mark':
                            clause.append(span_token.text)
                    if clause_flag:
                        clause_doc = self.nlp(' '.join(clause))
                        clause_doc = DependencyTreeUtil.merge_np_chunks(clause_doc)
                        clause_doc = DependencyTreeUtil.merge_np_of_np(clause_doc)
                        clause_relation_tuple_result = self.extract_from_text(clause_doc.text, doc_api_name)
                        statement_record_list.extend(clause_relation_tuple_result)
                feature_name = feature_span.text
                neg = False
                for f in feature_span:
                    if f.dep_ == "neg":
                        neg = not neg
                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, feature_span.root)
                lead_verb = ""
                for token in feature_span:
                    if token.head == token:
                        lead_verb = token
                extra_info = {
                    "condition": condition_text,
                    "core": feature_span.text,
                    "leading_verb": lead_verb.lemma_,
                    "neg": neg,
                    "compare_subject": '',
                    "compare_object": '',
                }
                feature_name = feature_name.replace(feature_span.root.text, feature_span.root.lemma_)
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
