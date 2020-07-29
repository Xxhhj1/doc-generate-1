import definitions
from pathlib import Path
import json

api_to_example_json_path = Path(definitions.ROOT_DIR) / "output" / "json" / "api_2_example_sorted.json"
mid_to_method_info_json_path = Path(definitions.ROOT_DIR) / "output" / "json" / "mid_2_method_info_without_comment.json"
mid_to_qualified_name_json_path = Path(definitions.ROOT_DIR) / "output" / "json" / "mid_2_qualified_name.json"


class JsonService:
    def __init__(self):
        self.methods_info = list() # mid对应每个方法的描述信息
        self.method_names = list() # mid对应每个方法的全限定名
        self.api_to_mid = dict() # 每个api对应的相关mid
        with open(api_to_example_json_path, 'r') as f:
            self.api_to_mid = json.load(f)

        methods = open(mid_to_method_info_json_path, 'r').readlines()
        for method in methods:
            self.methods_info.append(json.loads(method)['method'])

        method_names = []
        methods = open(mid_to_qualified_name_json_path, 'r').readlines()
        for method in methods:
            self.method_names.append(json.loads(method)['qname'])

    def api_as_parameter(self, qualified_name):
        result = list()
        mid_list: list = self.api_to_mid[qualified_name]
        key_word = qualified_name[qualified_name.rfind('.')+1:]
        for i in range(len(mid_list)):
            mid = mid_list[i]
            method_info: str = self.methods_info[mid - 1]
            method_name = self.method_names[mid - 1]
            para_str = method_info[method_info.find('('):method_info.find(')')]
            if method_info.find('{') != -1 and para_str.find(key_word) != -1:
                result.append(method_name)
        return result

    def api_as_return_value(self, qualified_name):
        result = list()
        mid_list: list = self.api_to_mid[qualified_name]
        key_word = qualified_name[qualified_name.rfind('.') + 1:]
        for i in range(len(mid_list)):
            mid = mid_list[i]
            method_info: str = self.methods_info[mid - 1]
            method_name = self.method_names[mid - 1]
            prefix = method_info[:method_info.find('(')]
            if method_info.find('{') != -1 and prefix.find(key_word) != -1:
                result.append(method_name)
        return result


if __name__ == '__main__':
    json_service = JsonService()
    print(len(json_service.api_as_parameter('org.jabref.model.entry.BibEntry')))
    print(len(json_service.api_as_return_value('org.jabref.model.entry.BibEntry')))
