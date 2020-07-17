from sekg.util.dependency_tree_util import DependencyTreeUtil

from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.statement_extractor import StatementExtractor


class VBNPStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "vb_np"
        self.condition_extractor_name = "behavior_vb_np"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        if not simple_sentence.valid_check():
            return statement_record_list
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_verb_NP(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                       doc_api_name))
        return statement_record_list

    def extract_for_A_verb_NP(self, sent_doc, subject, predicate, doc_api_name, allow_condition=False):
        statement_record_list = []
        is_than_flag = False
        has_than = False
        for than_token in sent_doc:
            if than_token.pos_ == 'ADV' and than_token.tag_ == 'RBR':
                is_than_flag = True
            if than_token.text == 'than':
                has_than = True
        if is_than_flag or has_than:
            # 是有比较级的形式，跳过
            return statement_record_list
        object = DependencyTreeUtil.get_object_for_verb(sent_doc, predicate)
        conj_predicate_list = DependencyTreeUtil.get_conj_predicate(sent_doc)
        for conj_predicate in conj_predicate_list:
            # 处理连词情况
            sub_sent_doc = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
            conj_statement_result = self.extract_for_A_verb_NP(sub_sent_doc,
                                                               subject,
                                                               conj_predicate,
                                                               doc_api_name)
            statement_record_list.extend(conj_statement_result)
        # 直接宾语
        if object is None:
            prep_object_list = DependencyTreeUtil.get_prep_object_for_preposition(sent_doc, predicate)
            if prep_object_list is not None and len(prep_object_list) > 0:
                prep_object = prep_object_list[0]
                prep_statement_result = self.extract_functionality_for_verb_noun_with_object(
                    sent_doc, subject, predicate, prep_object, doc_api_name, allow_condition)
                statement_record_list.extend(prep_statement_result)
            # 不包含宾语，即使是介词加宾语
            else:
                functionality_span = DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree(
                    sent_doc, subject.root, predicate)
                try:
                    if functionality_span is None or functionality_span.end_char == 0 or functionality_span.text == "":
                        return statement_record_list
                except Exception as e:
                    print(e)
                    return statement_record_list
                filter = ''
                for adv_token in functionality_span:
                    if adv_token.pos_ == 'ADV' and adv_token.text != 'not':
                        filter = adv_token
                functionality_filter = functionality_span
                if filter is not None and type(filter) != str:
                    functionality_filter = DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree(
                        sent_doc, filter, predicate)
                functionality_filter_swap_text = DependencyTreeUtil.swap_condition_to_end(sent_doc, predicate)
                span_two = functionality_filter_swap_text.split('$$')
                if len(span_two) > 1:
                    second = span_two[1].replace(subject.text, '', 1).strip()
                    functionality_filter_swap_text = span_two[0] + '' + second
                functionality_name = functionality_filter_swap_text.strip()
                neg = False
                if functionality_filter is None or functionality_filter.end_char == 0 or functionality_filter.text == "":
                    return statement_record_list
                if "not " in functionality_filter.text:
                    neg = True
                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, predicate)
                action_object = DependencyTreeUtil.get_action_text_for_token(sent_doc, object)
                if len(action_object) > 0:
                    action_object = action_object[0]
                else:
                    action_object = ""
                functionality_extra_info = {
                    "condition": condition_text,
                    "leading_verb": predicate.lemma_,
                    "neg": neg,
                    "action object": action_object,
                    "compare_subject": '',
                    "compare_object": '',
                }
                functionality_name = functionality_name.replace(predicate.text, predicate.lemma_).strip()
                info_from_set = set()
                info_from_set.add((ALLKnowledgeFromType.FROM_Text_Func, sent_doc.text, doc_api_name))
                extractor_name = self.extractor_name
                if self.check_has_condition(condition_text, functionality_name):
                    if not allow_condition:
                        return statement_record_list
                    extractor_name = self.condition_extractor_name
                relation_data_tuple = StatementRecord(subject.text,
                                                      RelationNameConstant.has_Functionality_Relation,
                                                      functionality_name,
                                                      NPEntityType.CategoryType,
                                                      NPEntityType.FunctionalityType,
                                                      extractor_name, info_from_set, **functionality_extra_info)
                statement_record_list.append(relation_data_tuple)

        else:
            object_relation_tuple_result = self.extract_functionality_for_verb_noun_with_object(
                sent_doc, subject, predicate, object, doc_api_name, allow_condition)
            statement_record_list.extend(object_relation_tuple_result)
        return statement_record_list

    def extract_functionality_for_verb_noun_with_object(self, sent_doc, subject, predicate, object, doc_api_name,
                                                        allow_condition=False):
        statement_record_list = []
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
        condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, predicate)
        action_object = DependencyTreeUtil.get_action_text_for_token(sent_doc, object)
        if len(action_object) > 0:
            action_object = action_object[0]
        else:
            action_object = ""
        if action_object == "":
            action_object = str(object)

        if predicate.lemma_.lower() in self.allow_like_word or predicate.lemma_.lower() in self.limit_like_word or predicate.lemma_.lower() in self.guarantee_like_word or predicate.lemma_.lower() in self.prohibit_like_word or predicate.lemma_.lower() in self.depend_on_like_word:
            return statement_record_list
        else:
            functionality_extra_info = {
                "condition": condition_text,
                "leading_verb": str(predicate.lemma_),
                "neg": neg,
                "action object": action_object,
                "compare_subject": '',
                "compare_object": '',
            }
            feature_statement_record_list, feature_for_functionality_name = self.get_feature_for_functionality(
                sent_doc, subject, predicate, doc_api_name)
            statement_record_list.extend(feature_statement_record_list)
            if len(feature_statement_record_list) > 0:
                functionality_name = functionality_name.replace(
                    feature_for_functionality_name, '')
            start_name = subject.text

            if subject.text.lower() == "you":
                start_name = doc_api_name
                functionality_name = functionality_name.rstrip("you")

            info_from_set = set()
            info_from_set.add((ALLKnowledgeFromType.FROM_Text_Func, sent_doc.text, doc_api_name))
            extractor_name = self.extractor_name
            if self.check_has_condition(condition_text, functionality_name):
                if not allow_condition:
                    return statement_record_list
                extractor_name = self.condition_extractor_name

            relation_data_tuple = StatementRecord(start_name,
                                                  RelationNameConstant.has_Functionality_Relation,
                                                  start_name + " " + functionality_name,
                                                  NPEntityType.CategoryType,
                                                  NPEntityType.FunctionalityType,
                                                  extractor_name, info_from_set, **functionality_extra_info)
            statement_record_list.append(relation_data_tuple)

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

        return statement_record_list, feature_name
