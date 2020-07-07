import unittest

from project.extractor_module.characteristic_structure_extractor import CharacteristicStructureExtractor

ce = CharacteristicStructureExtractor()
t = ce.split_method_name_into_words("StringBuffer")
print(t)
