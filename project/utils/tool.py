from sekg.util.dependency_tree_util import DependencyTreeUtil
import re
import pickle

from project.extractor_module.data_model.statement_record import StatementRecord


class Tool:
    @staticmethod
    def print_nlp_analysis(sent_doc):
        np_chunk_detail = [chunk for chunk in sent_doc.noun_chunks]
        print("np_chunk_detail for sentence", np_chunk_detail)
        SEP = " - "
        for chunk in sent_doc.noun_chunks:
            print(chunk.text, SEP, chunk.root.text, SEP,
                  chunk.root.dep_, SEP,
                  chunk.root.head.text)
        print("----chunk detail")
        for chunk in sent_doc.noun_chunks:
            for token in chunk:
                print(token.text, SEP, token.pos_, SEP, token.tag_, SEP)
        print("-----------end chunk print----------")
        for token in sent_doc:
            print(token.text, SEP, token.pos_, SEP, token.tag_, SEP, token.dep_, SEP, token.head.text, SEP,
                  token.head.pos_, SEP,
                  [child for child in token.children],
                  SEP,
                  [child for child in token.lefts],
                  SEP,
                  [child for child in token.rights],
                  )
        print("-----------end tree print----------")
        print("-----------subtree----------")
        print("subject of is:", DependencyTreeUtil.get_subject(doc=sent_doc),
              DependencyTreeUtil.get_subject_text(sent_doc))
        print("predicate is:", DependencyTreeUtil.get_main_predicate(doc=sent_doc))
        print("-----------end subtree----------")

    @staticmethod
    def save_2_pickle(data, path):
        """
        将结果序列化保存到文件
        :return:
        """
        print("save")
        with open(path, "wb") as file_handler:
            pickle.dump(data, file_handler, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_pickle(path):
        """
        将结果序列化保存到文件
        :return:
        """
        print(f"load{path}")
        with open(path, "rb") as file_handler:
            data = pickle.load(file_handler)
        return data

    @staticmethod
    def recover_name(text, api_from):
        text += " "
        prefix = "java"
        if api_from.find("android") >= 0:
            prefix = "android"
        if prefix == "java":
            matchObj = re.search(r'(java)-(.*?)-(.*?) ', text, re.M | re.I)
            if not matchObj:
                return text
            res = re.sub(r'(java)-(.*?)-(.*?) ', "the " + matchObj.group().replace("-", "."), text)
        else:
            matchObj = re.search(r'(android)-(.*?)-(.*?) ', text, re.M | re.I)
            if not matchObj:
                return text
            res = re.sub(r'(android)-(.*?)-(.*?) ', "the " + matchObj.group().replace("-", "."), text)
        res = res.replace("the the", "the")
        return res.strip()

    @staticmethod
    def check_api_related(statement_record: StatementRecord):
        # 判断抽取的结果是否是和API相关的
        return True

    @staticmethod
    def recover_name_process(statement_record):
        s_name = statement_record.s_name
        e_name = statement_record.e_name
        info_from_set = statement_record.info_from_set
        new_info_from_set = set()
        api_from = ""
        for info_from in info_from_set:
            t1, text, t3 = info_from
            api_from = t3
            text = Tool.recover_name(text, api_from)
            new_info_from_set.add((t1, text, t3))

        s_name = Tool.recover_name(s_name, api_from)
        e_name = Tool.recover_name(e_name, api_from)
        statement_record.s_name = s_name
        statement_record.e_name = e_name
        statement_record.info_from_set = new_info_from_set
        return statement_record

    @staticmethod
    def post_process(statement_record_list, check=True):
        recover_list = []
        for statement_record in statement_record_list:
            recover_list.append(Tool.recover_name_process(statement_record))
        if check:
            after_check_list = []
            for statement_record in recover_list:
                if Tool.check_api_related(statement_record):
                    after_check_list.append(statement_record)
            return after_check_list
        return recover_list
