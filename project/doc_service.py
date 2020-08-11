from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument

from project.utils.path_util import PathUtil


class DocService:
    def __init__(self):
        pro_name = "jabref"
        data_dir = PathUtil.doc(pro_name=pro_name, version="v1.2")
        self.doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)

    def extract_all_doc(self):
        text_list = []
        document_list = self.doc_collection.get_document_list()
        for doc in document_list:
            if doc.get_doc_text_by_field('full_description') != "":
                text_list.append(doc.get_doc_text_by_field('full_description'))
        return text_list

    # 根据api id返回相应dc文档中描述信息
    def get_doc_info(self, api_id):
        doc: MultiFieldDocument = self.doc_collection.get_by_id(api_id)
        result = dict()
        result['full_html_description'] = doc.get_doc_text_by_field('full_html_description')
        result['full_description'] = doc.get_doc_text_by_field('full_description')
        result['sentence_description'] = doc.get_doc_text_by_field('sentence_description')
        return result

    # 根据api id返回相应dc文件中的sample code
    def get_sample_code(self, api_id):
        doc: MultiFieldDocument = self.doc_collection.get_by_id(api_id)
        if doc is None:
            return None
        result = dict()
        sample_code = doc.get_doc_text_by_field('sample_code')
        for i in range(len(sample_code)):
            # sample_code[i] = "<br/>".join(sample_code[i].split("\n"))
            sample_code[i] = sample_code[i][2:]
        if sample_code is "":
            return None
        else:
            result['sample_code'] = sample_code
        return result


if __name__ == '__main__':
    doc_service = DocService()
    doc_service.extract_all_doc()
    # print(doc_service.get_sample_code(200))
