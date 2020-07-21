from sekg.ir.doc.wrapper import MultiFieldDocumentCollection

from project.utils.path_util import PathUtil


class DocService:
    def __init__(self):
        pro_name = "jabref"
        data_dir = PathUtil.doc(pro_name=pro_name, version="v1")
        self.doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)

    def extract_all_doc(self):
        text_list = []
        document_list = self.doc_collection.get_document_list()
        for doc in document_list:
            if doc.get_doc_text_by_field('full_description') != "":
                text_list.append(doc.get_doc_text_by_field('full_description'))
        return text_list


if __name__ == '__main__':
    doc_service = DocService()

    doc_service.extract_all_doc()
