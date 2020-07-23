from sekg.text.spacy_pipeline.pipeline import PipeLineFactory
from sekg.util.dependency_tree_util import DependencyTreeUtil
import re

from project.extractor_module.data_model.simple_sentence import SimpleSentence
from project.utils.statement_checking import APIRelatedChecking


class SimpleSentenceSplit:
    """
    给定一句话，返回这个句子中切分出来的简单句子列表，
    用SimpleSentence这个对象进行封装
    """

    def __init__(self, nlp=None):
        if nlp is not None:
            self.nlp = nlp
        else:
            self.nlp = PipeLineFactory.full_pipeline()
        self.mark_filter_words = {'if', 'when'}
        self.api_related_tool = APIRelatedChecking()

    def modify_api_qualified_name(self, text, api_from):
        prefix = "java"
        if api_from.find("android") >= 0:
            prefix = "android"
        if prefix == "java":
            matchObj = re.search(r'(java).(.*?).(.*?) ', text, re.M | re.I)
            if not matchObj:
                return text
            if matchObj.group().lower() == api_from.lower():
                return text
            res = re.sub(r'(java).(.*?).(.*?) ', "the " + matchObj.group().replace(".", "-"), text)
        else:
            matchObj = re.search(r'(android).(.*?).(.*?) ', text, re.M | re.I)
            if not matchObj:
                return text
            if matchObj.group().lower() == api_from.lower():
                return text
            res = re.sub(r'(android).(.*?).(.*?) ', "the " + matchObj.group().replace(".", "-"), text)
        res = res.replace("the the", "the")
        return res

    def check_api_related(self, text: str):
        return self.api_related_tool.check_is_api_related(text)

    def create_sentence_list(self, text, api_from=""):
        simple_sentence_list = []
        text = ' '.join(text.split())
        text = text.replace("is A ", "is a ")
        if not self.check_api_related(text):
            return simple_sentence_list
        text = self.modify_api_qualified_name(text, api_from)
        doc = self.self_doc(text)
        for sent_doc in doc.sents:
            sent_doc_list = self.clause_extraction(sent_doc.as_doc())
            for sent_doc_l in sent_doc_list:
                sent_doc_t = DependencyTreeUtil.merge_np_of_np(sent_doc_l)
                simple_sentence = SimpleSentence(api_from, doc, sent_doc_t)
                if self.check_simple_sentence_valid(simple_sentence):
                    simple_sentence_list.append(simple_sentence)
        return simple_sentence_list

    def check_simple_sentence_valid(self, simple_sentence: SimpleSentence):
        if simple_sentence.get_subject() is None or simple_sentence.get_predicate() is None:
            return False
        return True

    def clause_extraction(self, sent_doc):

        predicate = DependencyTreeUtil.get_main_predicate(sent_doc)
        subject = DependencyTreeUtil.get_subject(sent_doc)
        sent_doc_list = []
        if predicate is None or subject is None:
            return sent_doc_list
        for i, token in enumerate(sent_doc):
            if token.dep_ == 'conj' and token.pos_ == 'VERB' and token.head == predicate:
                # added = True
                conj_predicate_span = DependencyTreeUtil.get_subtree_span_from_one_token_index(sent_doc, i)
                is_complete = False
                # 判断是否有主语
                for nsubj_token in conj_predicate_span:
                    if nsubj_token.dep_.startswith('nsubj'):
                        is_complete = True
                        break
                if is_complete:
                    sent_doc_list.append(self.self_doc(conj_predicate_span.text))
                else:
                    clause_text = subject.text + ' ' + conj_predicate_span.text
                    sent_doc_list.append(self.self_doc(clause_text))
                sent_doc_list.append(self.self_doc(
                    DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree_for_split_sentence(
                        sent_doc, token, predicate).text))
                if sent_doc_list[1] is None or sent_doc_list[0].text == sent_doc_list[1].text:
                    return list(sent_doc_list[0])
                if sent_doc_list[0].text == sent_doc.text or sent_doc_list[1] == sent_doc.text:
                    return sent_doc_list
                final_sent_list = []
                for sent_doc_l in sent_doc_list:
                    final_sent_list.extend(self.clause_extraction(sent_doc_l))
                return final_sent_list
            if token.dep_ == 'relcl' and token.head.pos_ == 'NOUN':
                # added = True
                conj_predicate_span = DependencyTreeUtil.get_subtree_span_from_one_token_index(sent_doc, i)
                that_flag = False
                for index, conj_token in enumerate(conj_predicate_span):
                    if (conj_token.tag_ == 'WDT' or conj_token.tag_ == "DT") and (
                            conj_token.text == 'that' or conj_token.text == 'which'):
                        that_flag = True
                        if index > 1:
                            text = token.head.text + ' ' + conj_predicate_span[
                                                           0:index - 1].text + ' ' + conj_predicate_span[index + 1: len(
                                conj_predicate_span) + 1].text
                        else:
                            text = token.head.text + ' ' + conj_predicate_span[
                                                           index + 1: len(conj_predicate_span) + 1].text
                        sent_doc_list.append(self.self_doc(text))
                if not that_flag:
                    text_all = token.head.text + ' ' + conj_predicate_span.text
                    sent_doc_list.append(self.self_doc(text_all))
                sent_doc_list.append(self.self_doc(
                    DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree_for_split_sentence(
                        sent_doc, token, predicate).text))
                if sent_doc_list[1] is None or sent_doc_list[0].text == sent_doc_list[1].text:
                    return list(sent_doc_list[0])
                if sent_doc_list[0].text == sent_doc.text or sent_doc_list[1] == sent_doc.text:
                    return sent_doc_list
                final_sent_list = []
                for sent_doc_l in sent_doc_list:
                    final_sent_list.extend(self.clause_extraction(sent_doc_l))
                return final_sent_list
            if token.dep_ == 'mark' and token.tag_ == 'IN' and token.lemma_.lower() not in self.mark_filter_words:
                # added = True
                conj_predicate_span = DependencyTreeUtil.get_subtree_span_from_one_token_index(sent_doc, token.head.i)
                for index, conj_token in enumerate(conj_predicate_span):
                    if conj_token.dep_ == 'mark':
                        if index < len(conj_predicate_span) - 1 and conj_predicate_span[index + 1].dep_ == 'mark':
                            continue
                        else:
                            conj_predicate_span = conj_predicate_span[index + 1:]
                            break
                    if index < len(conj_predicate_span) - 1 and conj_predicate_span[index + 1].dep_ == 'mark':
                        continue
                doc1 = self.self_doc(conj_predicate_span.text)
                doc2 = DependencyTreeUtil.get_subtree_span_from_one_token_filter_another_token_sub_tree_for_split_sentence(
                    sent_doc, token.head, predicate)
                if doc2 is None:
                    sent_doc_list.append(doc1)
                    return sent_doc_list
                doc2 = self.self_doc(doc2.text)
                if doc1.text == doc2.text:
                    sent_doc_list.append(doc1)
                    return sent_doc_list
                sent_doc_list.append(doc1)
                sent_doc_list.append(doc2)
                if doc1.text == sent_doc.text or doc2.text == sent_doc.text:
                    return sent_doc_list
                final_sent_list = []
                for sent_doc_l in sent_doc_list:
                    final_sent_list.extend(self.clause_extraction(sent_doc_l))
                return final_sent_list
                # for mark_token in conj_predicate_span:
                # if mark_token.text != 'if':
        sent_doc_list.append(sent_doc)
        return sent_doc_list

    def self_doc(self, text):
        doc = self.nlp(text)
        doc = DependencyTreeUtil.merge_np_chunks(doc)
        doc = DependencyTreeUtil.merge_np_of_np(doc)
        return doc
