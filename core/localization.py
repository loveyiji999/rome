import yaml
import os

class Localization:
    def __init__(self, lang='zh'):
        file_path = os.path.join('assets', 'localization.yaml')
        with open(file_path, 'r', encoding='utf-8') as file:
            self.data = yaml.safe_load(file)[lang]

    def translate(self, module, attribute):
        return self.data['car_attributes'][module][attribute]
