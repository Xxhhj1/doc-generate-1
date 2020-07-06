import operator
import re

from sekg.text.pretreatment.complete_subject import PipeLineFactory
from sekg.util.code import CodeElementNameUtil


class ReferenceResolution:
    def __init__(self):
        self.nlp = PipeLineFactory.full_pipeline_for_coreference_resolution()
        self.code_element_name_util = CodeElementNameUtil()

    @staticmethod
    def replace_with_start_end(start, end, word, text):
        """
        根据起点和终点替换字符串
        :param start:
        :param end:
        :param word:
        :param text:
        :return:
        """
        result = text[:start] + word + text[end:]
        return result

    @staticmethod
    def replace_word_in_string(name_replace_list, text):
        """
        根据起始位置、终止位置、替换单词
        :param name_replace_list:
        :param text:
        :return:
        """
        result = text
        name_replace_list.sort(key=operator.itemgetter(0), reverse=True)
        for name_replace in name_replace_list:
            start_pos, end_pos, old_word, new_word = name_replace
            result = ReferenceResolution.replace_with_start_end(start_pos, end_pos, new_word, result)
        return result

    @staticmethod
    def word_num(text):
        """
        有多少个词
        :param text:
        :return: num int
        """
        return len(str(text).split(" "))

    def lemma_word(self, word):
        """
        词性还原
        :param word:
        :return:
        """
        doc = self.nlp(word)
        result = []
        for token in doc:
            if token.lemma_ == "-PRON-":
                result.append(token.norm_)
            else:
                result.append(token.lemma_)
        return " ".join(result)

    def maybe_contain_api(self, name):
        """
        判断name里面是否可能包含API
        :param name:
        :return: True or False
        """
        if name is None or str(name) == "":
            return False

        uncamelize = self.code_element_name_util.uncamelize(name.strip()).replace("( ", "(")
        if len(name.strip().split(" ")) < len(uncamelize.strip().split(" ")) or self.check_upper_case(name):
            return True
        return False

    def check_pronoun(self, word):
        pronoun_set = {
            "it", "that", "this", "these", "those",
            "which", "one", "ones", "they", "other", "another"
        }
        for n in str(word).split(" "):
            if n in pronoun_set:
                return True

        doc = self.nlp(word)
        for token in doc:
            if token.lemma_ == '-PRON-':
                return True

        return False

    @staticmethod
    def replace_ignore_case(text, old, new, ):
        reg = re.compile(re.escape(old), re.IGNORECASE)
        return str(reg.sub(new, text))

    def alias_name_of_qualified_name(self, qn):
        if str(qn).find("(") > 0:
            return qn
        last_part = str(qn).split(".")[-1]
        return self.code_element_name_util.uncamelize(last_part)

    def may_be_api(self, name):
        """
        判断一个名字是不是特别像API
        :param name:
        :return:
        """
        if str(name).strip().find(" ") > 0:
            return False
        if len(str(name).split(".")) >= 3:
            return True

    def remove_reference_with_context(self, context, text, input_doc=None):
        """

        :param input_doc:
        :param context: 一个字典，可以传入方法需要的上下文信息，
        package 信息，class信息，method信息，文档归属对象类型
        :param text: 文本
        :return: text，每句话的改动
        """
        doc_belong_api_name = context["qn"]
        alias = self.alias_name_of_qualified_name(doc_belong_api_name)
        # 按照词数目进行过滤
        skip_size = 4
        may_be_class_set = {"this class", "the class", "this interface", "this abstract class", "the interface",
                            "this implementation"}
        my_be_method_set = {"this method ", "the method "}
        if doc_belong_api_name.find("(") < 0:
            for name in may_be_class_set:
                text = ReferenceResolution.replace_ignore_case(text, name, doc_belong_api_name)
        else:
            flag = True
            for my_be_method in my_be_method_set:
                sp_list = text.lower().split(my_be_method)
                if len(sp_list) > 1:
                    ssp_list = sp_list[-1].split(" ")
                    if len(ssp_list) > 0:
                        if ssp_list[0].find("(") < 0:
                            flag = False
                if flag:
                    text = ReferenceResolution.replace_ignore_case(text, my_be_method, doc_belong_api_name + " ")
                    break
        # print(text)
        text = ReferenceResolution.replace_ignore_case(text, "it is recommended that ", "recommended that ")
        text = ReferenceResolution.replace_ignore_case(text, "it will be ", doc_belong_api_name + " will be ")
        if input_doc is None:
            doc = self.nlp(text)
        else:
            doc = input_doc
        row = doc.text
        result = []
        if doc._.coref_clusters is None:
            return row
        all_new_word_list = []
        for cluster in doc._.coref_clusters:
            try:
                new_word = cluster.main.text
                if ReferenceResolution.word_num(new_word) >= skip_size:
                    continue
                for men in cluster.mentions:
                    if cluster.main.text == men.text:
                        continue
                    old_word = men.text
                    start_pos = men.start_char
                    end_pos = men.end_char
                    if new_word == "":
                        continue
                    # 判断old_word是否已经是API了,已经是了就不替换
                    if self.lemma_word(old_word) == self.lemma_word(
                            new_word):
                        continue
                    # 判断old_word是否是代词，不是就continue
                    if not self.check_pronoun(old_word):
                        continue
                    # 判断new_word是否是API
                    if new_word.lower().find(alias.lower()) < 0 and new_word.lower().find(
                            doc_belong_api_name.lower()) < 0:
                        continue

                    all_new_word_list.append(new_word)
                    result.append((start_pos, end_pos, old_word, new_word))
            except Exception as e:
                print(e)
        tmp_after_text = ReferenceResolution.replace_word_in_string(result, row)
        # print(tmp_after_text)
        new_result_list = []
        doc = self.nlp(tmp_after_text)
        for np in doc.noun_chunks:
            for new_word in all_new_word_list:
                pos = str(np.text).find(new_word)
                if pos > 0:
                    new_new_word = ". " + new_word
                    start_pos = np.start_char + pos
                    end_pos = np.end_char
                    new_result_list.append((start_pos, end_pos, new_word, new_new_word))
        after_text = ReferenceResolution.replace_word_in_string(new_result_list, tmp_after_text)

        if doc_belong_api_name.find("(") > 0:
            for my_be_method in my_be_method_set:
                after_text = ReferenceResolution.replace_ignore_case(after_text, my_be_method,
                                                                     " " + doc_belong_api_name + " ")
        else:
            for may_be_class in may_be_class_set:
                after_text = ReferenceResolution.replace_ignore_case(after_text, may_be_class, doc_belong_api_name)

        return after_text, result

    @staticmethod
    def check_upper_case(text):
        """
        判断文本里面是否包含了驼峰式的class
        :param text:
        :return:
        """
        splited = str(text).split(" ")
        for i, s in enumerate(splited):
            if i > 0 and s[0].isupper():
                return True
        return False


if __name__ == '__main__':
    reference_resolution_tool = ReferenceResolution()
    context = {"qn": 'java.applet.AppletContext'}
    reference_resolution_tool. \
        remove_reference_with_context(context,
                                      'The methods in this interface can be used by an applet to obtain information about its environment.')
