# -*- encoding: utf-8 -*-

from simple.czsc import CzscModelEngine

class FactorAbstract:
    def __init__(self, czsc: CzscModelEngine):
        self.czsc = czsc

    def execute(self):
        pass

    def get_factor_name(self):
        return 'abstract'
