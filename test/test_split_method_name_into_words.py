import unittest

from project.module1.characteristic_structure_extractor import CharacteristicStructureExtractor

ce = CharacteristicStructureExtractor()
t = ce.split_method_name_into_words("StringBuffer")
print(t)
