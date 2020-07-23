import pickle
from pathlib import Path

from definitions import OUTPUT_DIR
from bs4 import BeautifulSoup
import os


class UserManual:
    def __init__(self):
        self.base_path = Path(OUTPUT_DIR) / "user_manual"

    def extract_md(self, md_file):
        with open(md_file, "r", encoding='utf-8') as file_obj:
            content = file_obj.read()
            content = (content.replace("#", ""))
            return content

    def get_files(self):
        file_names = [os.path.join(path, file_name)
                      for path, _, file_list in os.walk(str(self.base_path))
                      for file_name in file_list if file_name.endswith('.md')]
        return file_names

    def extract_all(self):
        file_names = self.get_files()
        res = []
        for file_path in file_names:
            res.append(self.extract_md(file_path))
        self.save(res)
        return res

    def save_2_pickle(self, path, res):
        """
        将结果序列化保存到文件
        :return:
        """
        with open(path, "wb") as file_handler:
            pickle.dump(res, file_handler, protocol=pickle.HIGHEST_PROTOCOL)

    def save(self, res):
        self.save_2_pickle(str(Path(OUTPUT_DIR) / "user_manual.pickle"), res)


if __name__ == '__main__':
    user_manual_service = UserManual()
    user_manual_service.extract_all()
