from sekg.util.dependency_tree_util import DependencyTreeUtil

from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.rule_model.behavior.behavior_vb_np_extractor import BehaviorVBNPStatementExtractor
from model.statement_extractor import StatementExtractor


class FuncCompareStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "fun_compare"
        self.vb_np = BehaviorVBNPStatementExtractor()
        self.compare_word_set = {
            "same as", "equivalent to", "similar as", "similar to", "like",
            "different from", "unlike"
        }

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_functionality_compare(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                               doc_api_name))

        return statement_record_list

    def extract_functionality_compare(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if not self.is_func_compare_template(sent_doc, subject, predicate):
            return statement_record_list
        return self.extract_for_A_is_xxx(sent_doc, subject, predicate, doc_api_name)

    def is_func_compare_template(self, sent_doc, subject, predicate):
        if predicate.lemma_ == "be" and (predicate.pos_ == "VERB" or predicate.pos_ == "AUX"):
            for word in self.compare_word_set:
                if sent_doc.text.find(word) >= 0:
                    return True
        return False

    def extract_for_A_is_xxx(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
        neg = False
        # Tool.print_nlp_analysis(sent_doc)
        subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
        for f in subtree_span:
            if f.dep_ == "neg":
                neg = not neg
        if attr_span is not None:
            flag = False
            if attr_span.root.lemma_.lower() in self.same_word_list:

                condition_text = DependencyTreeUtil.get_conditions_text_for_token(sent_doc, predicate)
                object = DependencyTreeUtil.get_object_for_verb(sent_doc, predicate)
                action_object = ''
                if object is not None:
                    action_object = DependencyTreeUtil.get_action_text_for_token(sent_doc, object)
                if len(action_object) > 0:
                    action_object = action_object[0]
                else:
                    action_object = ""
                verb = ''
                name = ''
                if attr_span.root.text.find('equivalent') >= 0:
                    verb = 'is same as'
                    name = attr_span.text.replace('equivalent', 'same').replace('to', 'as', 1)
                    flag = True
                elif attr_span.root.text.find('same') >= 0:
                    verb = 'is same as'
                    name = attr_span.text
                    flag = True
                elif attr_span.root.text.find("similar") >= 0:
                    verb = 'is similar to'
                    name = attr_span.text
                    flag = True
                elif attr_span.root.text.find("different") >= 0:
                    verb = 'is different from'
                    name = attr_span.text
                    flag = True
                if not flag:
                    return statement_record_list
                functionality_extra_info = {
                    "condition": condition_text,
                    "leading_verb": verb,
                    "neg": neg,
                    "action object": action_object,
                    "compare_subject": subject.root.text,
                    "compare_object": "",
                }

                info_from_set = set()
                info_from_set.add((ALLKnowledgeFromType.FROM_Text_Func, sent_doc.text, doc_api_name))
                relation_data_tuple = StatementRecord(subject.text,
                                                      RelationNameConstant.Functionality_Compare_Relation,
                                                      name,
                                                      NPEntityType.CategoryType,
                                                      NPEntityType.FunctionalityCompareType,
                                                      self.extractor_name, info_from_set,
                                                      **functionality_extra_info)
                statement_record_list.append(relation_data_tuple)
                return statement_record_list
        else:
            for t in predicate.rights:
                for word in self.compare_word_set:
                    if t.text.find(word) >= 0:
                        name = t.text
                        for child in t.children:
                            if child.tag_.find("N") >= 0 and child.dep_ == 'pobj':
                                functionality_extra_info = {
                                    "condition": "",
                                    "leading_verb": word,
                                    "neg": neg,
                                    "action object": "",
                                    "compare_subject": subject.root.text,
                                    "compare_object": child.text,
                                }

                                info_from_set = set()
                                info_from_set.add((ALLKnowledgeFromType.FROM_Text_Func, sent_doc.text, doc_api_name))
                                relation_data_tuple = \
                                    StatementRecord(subject.text,
                                                    RelationNameConstant.Functionality_Compare_Relation,
                                                    name + " " + child.text,
                                                    NPEntityType.CategoryType,
                                                    NPEntityType.FunctionalityCompareType,
                                                    self.extractor_name, info_from_set,
                                                    **functionality_extra_info)
                                statement_record_list.append(relation_data_tuple)
        return statement_record_list
