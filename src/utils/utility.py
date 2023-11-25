import pandas as pd

def preprocess_order(df, all_order_id):

    order_pool = pd.DataFrame(columns=['order_id','total_weight','num_of_aisle','num_of_item'])

    for i, order_id in enumerate(all_order_id):
        total_weight = round(df[df['OrderID']==order_id].Weight.sum(), 2)
        num_of_aisle = df[df['OrderID']==order_id].ki.unique().shape[0]
        num_of_item = df[df['OrderID']==order_id].shape[0]

        order_pool.loc[i] = pd.Series({'order_id':order_id, 'total_weight':total_weight,
                                       'num_of_aisle':num_of_aisle, 'num_of_item':num_of_item})

    order_pool = order_pool.sort_values(by=['num_of_aisle','total_weight'])

    return order_pool


def select_seed_order(batch, current_order_pool, order_pool, rule_X):

    if rule_X == 'rule_A':
        batch.append(current_order_pool.iloc[0]['order_id'])
        new_current_order_pool = current_order_pool.drop(current_order_pool.iloc[0].name)
    else:
        last_seed_order = order_pool[order_pool['order_id']==batch[-1]]
        current_num_of_aisle = None
        temp_num_of_aisle = last_seed_order['num_of_aisle']

        while temp_num_of_aisle < 5:
            temp_num_of_aisle += 1
            same_aisle_orders = current_order_pool[current_order_pool['num_of_aisle']==temp_num_of_aisle]
            if len(same_aisle_orders) > 0:
                current_num_of_aisle = temp_num_of_aisle
                break

        if current_num_of_aisle is not None:
            batch.append(same_aisle_orders.iloc[0]['order_id'])
            new_current_order_pool = current_order_pool.drop(same_aisle_orders.iloc[0].name)
        else:
            batch.append(current_order_pool.iloc[0]['order_id'])
            new_current_order_pool = current_order_pool.drop(current_order_pool.iloc[0].name)

    return batch, new_current_order_pool


def select_accompanying_order(batch, current_order_pool, order_pool, rule_X):
    pass


def find_picking_time(batch, order_id_df):

    batch_info = order_id_df.loc[batch]
    max_ki = batch_info.ki.max()
    Qb = batch_info.ki.unique().shape[0]

    picking_time = (2*(max_ki-1)*1.2 + Qb*3)/0.5

    return picking_time


def find_packing_time(batch, order_pool):

    total_item_of_batch = 0
    for order_id in batch:
        total_item_of_batch += order_pool[order_pool['order_id']==order_id].iloc[0]['num_of_item']

    packing_time = len(batch)*15 + total_item_of_batch*2

    return packing_time


def set_rule_X():

    return 'rule_A'
