"""

对方法进行分类
将方法分为: accessor, mutator, creational, constructor, undefined五类

"""

from sekg.graph.exporter.graph_data import GraphData, NodeInfo
from project.utils.path_util import PathUtil
from nltk.corpus import wordnet as wn

pro_name = "jabref"
graph_data_path = PathUtil.graph_data(pro_name=pro_name, version="v1.4")
graph_data: GraphData = GraphData.load(graph_data_path)

accessor_key_word = ("get", "toString", "find", "search", "test", "contains", "is", "has", "show")
mutator_key_word = ("set", "add", "delete", "move", "remove", "parse", "insert", "extract", "open")
creational_key_word = ("copy", "construct", "create")
nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
verbs = {x.name().split('.', 1)[0] for x in wn.all_synsets('v')}


def get_pure_method_name_without_parameter(qualified_name=None):
    if qualified_name is None or qualified_name is "":
        raise ValueError("qualified name needed")
    qualified_name = qualified_name[:qualified_name.find("(")]
    result = qualified_name[qualified_name.rfind(".")+1:]
    return result


# 根据一系列的key word去做最基本的划分
def basic_classification(qualified_name=None):
    method_name: str = get_pure_method_name_without_parameter(qualified_name)
    # 大写开头的方法是构造器
    if method_name[0]<'a':
        return "constructor"
    if method_name.startswith(accessor_key_word):
        return "accessor"
    if method_name.startswith(mutator_key_word):
        return "mutator"
    if method_name.startswith(creational_key_word):
        return "creational"
    # return classification_according_to_return_type(qualified_name)
    return "undefined"


def classification_according_to_part_of_speech(qualified_name=None):
    first_word = split(camel_case=qualified_name)
    if first_word in verbs:
        return "mutator"
    if first_word in nouns:
        return "accessor"
    return "undefined"


def split(camel_case: str):
    result = camel_case[camel_case.rfind(".")+1:camel_case.find("(")]
    for i in range(len(result)):
        if result[i] < 'a':
            result = result[:i]
            break;
    return result


# 根据返回值去划分, 默认返回值为boolean类型划为accessor
def classification_according_to_return_type(qualified_name=None):
    qualified_name = qualified_name[:qualified_name.rfind('(')]
    print(qualified_name)
    node: NodeInfo = graph_data.find_one_node_by_property_value_starts_with(property_name="qualified_name", property_value_starter=qualified_name)
    boolean_node: NodeInfo = graph_data.find_nodes_by_ids(8)[0]
    print(node)
    print(boolean_node)
    if graph_data.exist_relation(node['id'], 'type of', 8):
        return "accessor"
    return "degenerate"


if __name__ == '__main__':
    # print(basic_classification("org.jabref.model.search.rules.MockSearchMatcher.isMatch(BibEntry entry)"))
    print(classification_according_to_return_type("org.jabref.logic.importer.fileformat.PdfContentImporterTest.testGetDescription()"))

