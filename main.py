import pandas as pd
from src.utils.utility import preprocess_order, select_seed_order, select_accompanying_order, set_rule_X, find_picking_time, find_packing_time

class BatchesGenerating():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if BatchesGenerating.__instance__ == None:
            BatchesGenerating()
        return BatchesGenerating.__instance__
    
    def __init__(self):
        if BatchesGenerating.__instance__ != None:
            raise Exception("Batches Generating is a singleton!")
        else:
            BatchesGenerating.__instance__ == self

            # center-to-center distance between two aisle (m)
            self.W = 2
            # length of aisle (m)
            self.L = 3
            # traveling speed of pickers (m/s)
            self.v_travel = 0.5
            # scanning time of each item (s)
            self.t_scan = 2
            # packing time of each order (s)
            self.t_pack = 15
            # the capacity of one picking cart (kg)
            self.capacity = 60


    def generate_batches(self, df):

        df.dropna(inplace=True)

        all_order_id = df.OrderID.unique()
        order_pool = preprocess_order(df, all_order_id)

        order_id_df = df.copy()
        order_id_df.set_index('OrderID', inplace=True)
        current_order_pool = order_pool.copy()
        # current_order_pool = current_order_pool.drop(current_order_pool.iloc[0].name)
        # print(order_id_df)
        # print(current_order_pool)
        # print(order_pool.iloc[1]['order_id'])
        
        batches = []

        # set the seed-order selection rule
        rule_X = 'rule_A'

        # batch = ['717HD145170', '123HD145170', '130HD145171']
        # packing_time = find_packing_time(batch, order_pool)
        # picking_time = find_picking_time(batch, order_id_df)
        # print(f'packing_time: {packing_time}')
        # print(f'picking_time: {picking_time}')

        while len(current_order_pool) > 0:
            # create empty bacth
            batch = []
            # select seed order
            batch, current_order_pool = select_seed_order(batch, current_order_pool, order_pool, rule_X)
            # select accompanying order
            weight_of_cart = 0
            while weight_of_cart < 60:
                if len(current_order_pool) == 0:
                    break

                batch, current_order_pool = select_accompanying_order(batch, current_order_pool, df, order_id_df)
                weight_of_cart += order_pool[order_pool['order_id']==batch[-1]].iloc[0]['total_weight']
            
            rule_X = set_rule_X()

            batches.append(batch)
        
        print(batches)

        return batches


if __name__ == "__main__":
    df = pd.read_csv('data/order_data.csv')
    paper_ocr = BatchesGenerating()
    batch = paper_ocr.generate_batches(df)
