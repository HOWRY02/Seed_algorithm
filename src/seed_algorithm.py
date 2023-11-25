import pandas as pd


class SeedAlgorithm():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if SeedAlgorithm.__instance__ == None:
            SeedAlgorithm()
        return SeedAlgorithm.__instance__

    def __init__(self):
        if SeedAlgorithm.__instance__ != None:
            raise Exception('Seed Algorithm is a singleton!')
        else:
            SeedAlgorithm.__instance__ = self
        
        
    def seed_order_selection_rule_A(self):
        pass

    def seed_order_selection_rule_B(self):
        pass

    def control_strategy_1(self):
        pass

    def control_strategy_2(self):
        pass


