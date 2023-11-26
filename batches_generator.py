import pandas as pd
from utils.utility import preprocess_order, select_accompanying_order, check_situation, find_picking_time, find_packing_time

class BatchesGenerator():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if BatchesGenerator.__instance__ == None:
            BatchesGenerator()
        return BatchesGenerator.__instance__
    
    def __init__(self):
        if BatchesGenerator.__instance__ != None:
            raise Exception("Batches Generating is a singleton!")
        else:
            BatchesGenerator.__instance__ == self

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
            self.current_num_of_aisle = None


    def generate_batches(self, df):

        # remove all Nan
        df.dropna(inplace=True)

        all_order_id = df.OrderID.unique()
        order_pool = preprocess_order(df, all_order_id)

        order_id_df = df.copy()
        order_id_df.set_index('OrderID', inplace=True)
        current_order_pool = order_pool.copy()
        
        batches = []

        # set the seed-order selection rule
        rule_X = 'rule_A'

        # set list of time
        picking_time_list = []
        packing_time_list = []

        while len(current_order_pool) > 0:

            temp_order_pool = current_order_pool.copy()
            # create empty batch
            batch = []
            temp_batch = []

            # select seed order
            seed_order, temp_order_pool = self.select_seed_order(batches, order_pool, temp_order_pool, rule_X)
            temp_batch.append(seed_order)

            if seed_order is not None:
                weight_of_cart = order_pool[order_pool['order_id']==temp_batch[-1]].iloc[0]['total_weight']
            
            # select accompanying orders
            while seed_order is not None:
                if len(current_order_pool) == 0:
                    break

                if len(temp_order_pool) == 0:
                    batch = temp_batch
                    current_order_pool = temp_order_pool
                    picking_time_list.append(find_picking_time(batch, weight_of_cart, order_id_df,
                                                               self.W, self.L, self.v_travel))
                    packing_time_list.append(find_packing_time(batch, weight_of_cart, order_pool,
                                                               self.t_scan, self.t_pack))
                    break

                accompanying_order = select_accompanying_order(temp_batch, temp_order_pool, df, order_id_df)
                temp_weight_of_cart = weight_of_cart + order_pool[order_pool['order_id']==accompanying_order].iloc[0]['total_weight']

                if temp_weight_of_cart < self.capacity:
                    temp_batch.append(accompanying_order)
                    temp_order_pool = temp_order_pool.drop(temp_order_pool[temp_order_pool['order_id']==accompanying_order].iloc[0].name)
                    weight_of_cart = temp_weight_of_cart

                else:
                    temp_picking_time = find_picking_time(temp_batch, weight_of_cart, order_id_df,
                                                          self.W, self.L, self.v_travel)

                    situation = check_situation(picking_time_list, packing_time_list,
                                                temp_picking_time)

                    # consider current situation
                    if situation == 'blocking':
                        rule_X = 'rule_B'
                    else:
                        rule_X = 'rule_A'
                        batch = temp_batch
                        current_order_pool = temp_order_pool
                        picking_time_list.append(find_picking_time(batch, weight_of_cart, order_id_df,
                                                                   self.W, self.L, self.v_travel))
                        packing_time_list.append(find_packing_time(batch, weight_of_cart, order_pool,
                                                                   self.t_scan, self.t_pack))

                    break

            # check if batch contains orders
            if len(batch) > 0:
                batches.append(batch)
                self.current_num_of_aisle = None
        
        C_max = sum(packing_time_list) + picking_time_list[0]
        num_of_item_in_batches = 0
        for i in batches:
            num_of_item_in_batches += len(i)

        print(f'picking_time_list: {picking_time_list, len(picking_time_list)}')
        print(f'packing_time_list: {packing_time_list, len(packing_time_list)}')
        print(f'C_max: {C_max}')
        print(batches, len(batches))
        print(num_of_item_in_batches)

        return batches


    def select_seed_order(self, batches, order_pool, temp_order_pool, rule_X):

        seed_order = None
        if rule_X == 'rule_B':
            if self.current_num_of_aisle is None:
                last_seed_order = order_pool[order_pool['order_id']==batches[-1][0]]
                print(last_seed_order)
                self.current_num_of_aisle = last_seed_order.iloc[0].num_of_aisle

            self.current_num_of_aisle += 1
            if self.current_num_of_aisle > 5:
                self.current_num_of_aisle = 1

            same_aisle_orders = temp_order_pool[temp_order_pool['num_of_aisle']==self.current_num_of_aisle]
            if len(same_aisle_orders) > 0:
                seed_order = same_aisle_orders.iloc[0]['order_id']
                temp_order_pool = temp_order_pool.drop(same_aisle_orders.iloc[0].name)
        else:
            seed_order = temp_order_pool.iloc[0]['order_id']
            temp_order_pool = temp_order_pool.drop(temp_order_pool.iloc[0].name)

        return seed_order, temp_order_pool

if __name__ == "__main__":
    df = pd.read_csv('data/order_data.csv')
    paper_ocr = BatchesGenerator()
    batch = paper_ocr.generate_batches(df)
