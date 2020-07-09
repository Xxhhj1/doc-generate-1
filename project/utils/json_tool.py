# 将statement结果保存成json形式，方便查看
from project.extractor_module.data_model.statement_record import StatementRecord

import json


class JsonTool:
    def __init__(self):
        self.json_collection = []

    def add_statement(self, api_id, relation_data_tuple: StatementRecord):
        d = relation_data_tuple.to_json()
        d["api_id"] = api_id
        self.json_collection.append(d)

    def save_json(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.json_collection, f, ensure_ascii=False, indent=4)
