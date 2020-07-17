from sekg.util.dependency_tree_util import DependencyTreeUtil

from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.rule_model.behavior.behavior_vb_np_extractor import BehaviorVBNPStatementExtractor
from model.statement_extractor import StatementExtractor


class BehaviorBeVBNStatementExtractor(StatementExtractor):
    # AE be VBN ((ADP) NP)+ COND
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "behavior_be_vbn"
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
        if predicate.pos_ == "VERB" and predicate.tag_ == "VBN":
            return True
        return False

    def extract_for_verb(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        span_object = DependencyTreeUtil.get_object_of_preposition_by(sent_doc)
        if span_object is None:
            action_object = ""
        else:
            action_object = DependencyTreeUtil.get_action_text_for_token(sent_doc, span_object.root)

        functionality_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
        neg = False
        for token in functionality_span:
            if token.dep_ == "neg":
                neg = not neg

        condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, predicate)
        if len(action_object) > 0:
            action_object = action_object[0]
        else:
            action_object = ""

        functionality_extra_info = {
            "condition": condition_text,
            "leading_verb": predicate.lemma_,
            "neg": neg,
            "action_object": action_object,
            "compare_subject": '',
            "compare_object": '',
        }
        if span_object is not None and str(span_object.text).endswith("s"):
            prefix = " doesn't "
        else:
            prefix = " don't "

        subject_name = subject.text
        if len(subject_name) > 1:
            # 原来的主语作为宾语，处理大小写问题
            subject_name = subject_name[0].lower() + subject_name[1:len(subject_name)]
        verb_text = predicate.lemma_

        if span_object is not None and not str(span_object.text).endswith("s"):
            verb_text = self.inflect_engine.plural(verb_text)
        if span_object is not None:
            span_object_text = span_object.text
        else:
            span_object_text = ""
        if "not " in functionality_span.text or "n't " in functionality_span.text:
            functionality_name = span_object_text + prefix + verb_text + " " + subject_name
        else:
            functionality_name = span_object_text + "  " + verb_text + " " + subject_name
        feature_statement_record_list, feature_for_functionality_name = self.vb_np.get_feature_for_functionality(
            sent_doc, subject, predicate, doc_api_name)
        functionality_name = " ".join(functionality_name.split())
        if len(feature_statement_record_list) > 0:
            functionality_name = functionality_name.replace(
                feature_for_functionality_name, '')
        start_name = subject.text

        if subject.text.lower() == "you":
            start_name = doc_api_name
            functionality_name = functionality_name.rstrip("you")
        if not self.check_has_condition(condition_text, functionality_name):
            return statement_record_list
        info_from_set = set()
        info_from_set.add((ALLKnowledgeFromType.FROM_Text_Func, sent_doc.text, doc_api_name))
        relation_data_tuple = StatementRecord(start_name,
                                              RelationNameConstant.has_Functionality_Relation,
                                              functionality_name,
                                              NPEntityType.CategoryType,
                                              NPEntityType.FunctionalityType,
                                              self.extractor_name, info_from_set, **functionality_extra_info)
        statement_record_list.append(relation_data_tuple)
        statement_record_list.extend(feature_statement_record_list)
        return statement_record_list
