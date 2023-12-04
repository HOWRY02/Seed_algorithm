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


def select_accompanying_order(batch, current_order_pool, df, order_id_df):

    batch_info = order_id_df.loc[batch]
    aisle_list_of_batch = set(batch_info.ki.unique())

    orders_id = current_order_pool.order_id.unique()
    list_point = []
    for order_id in orders_id:
        order_info = df[df['OrderID']==order_id]
        aisle_list_of_order = set(order_info.ki.unique())

        intersection_order_batch = aisle_list_of_order.intersection(aisle_list_of_batch)
        union_order_batch = aisle_list_of_order.union(aisle_list_of_batch)

        sim_i = len(intersection_order_batch)/len(union_order_batch)
        list_point.append([order_id, sim_i])

    list_point.sort(key = lambda x: x[1], reverse=True)

    accompanying_order = list_point[0][0]

    return accompanying_order


def find_picking_time(batch, weight_of_cart, order_id_df, W, L, v_travel):

    batch_info = order_id_df.loc[batch]
    max_ki = batch_info.ki.max()
    Qb = batch_info.ki.unique().shape[0]

    picking_time = (2*(max_ki-1)*W + Qb*L)/v_travel + 6*weight_of_cart

    return picking_time, max_ki, Qb


def find_packing_time(batch, weight_of_cart, order_pool, t_scan, t_pack):

    total_item_of_batch = 0

    for order_id in batch:
        total_item_of_batch += order_pool[order_pool['order_id']==order_id].iloc[0]['num_of_item']

    packing_time = len(batch)*t_pack + total_item_of_batch*t_scan

    return packing_time, total_item_of_batch


# def check_situation(picking_time_list, packing_time_list, temp_picking_time):

#     # Cn_1 = sum(picking_time_list) + temp_picking_time
#     # if len(picking_time_list) == 0:
#     #     Cn1_2 = 0
#     #     Cn2_2 = 0
#     # elif len(picking_time_list) == 1:
#     #     Cn1_2 = picking_time_list[0]
#     #     Cn2_2 = 0
#     # else:
#     #     Cn1_2 = sum(packing_time_list) + picking_time_list[0]
#     #     Cn2_2 = sum(packing_time_list[:-1]) + picking_time_list[0]

#     current_situation = None

#     if Cn_1 < Cn2_2:
#         current_situation = 'blocking'
#     elif Cn2_2 < Cn_1 and Cn_1 < Cn1_2:
#         current_situation = 'coordination'
#     else:
#         current_situation = 'starving'

#     return current_situation

def check_situation(picking_time_list, packing_time_list, temp_picking_time):

    # Cn_1 = picking_time_list[-1] + temp_picking_time

    if len(picking_time_list) == 0:
        Cn_1 = temp_picking_time
        Cn1_2 = 0
        Cn2_2 = 0
    elif len(picking_time_list) == 1:
        Cn_1 = picking_time_list[-1] + temp_picking_time
        Cn1_2 = packing_time_list[-1]
        Cn2_2 = 0
    else:
        Cn_1 = picking_time_list[-1] + temp_picking_time
        Cn1_2 = packing_time_list[-1]
        Cn2_2 = packing_time_list[-2]

    current_situation = None

    if Cn_1 < Cn2_2:
        current_situation = 'blocking'
    elif Cn2_2 < Cn_1 and Cn_1 < Cn1_2:
        current_situation = 'coordination'
    else:
        current_situation = 'starving'

    return current_situation

def find_completion_time(picking_time_list, packing_time_list, picking_time, packing_time):

    if len(picking_time_list) == 0:
        Cn_1 = picking_time
        Cn_2 = Cn_1 + packing_time
    else:
        Cn_1 = picking_time_list[-1] + picking_time
        Cn_2 = max(Cn_1,packing_time_list[-1]) + packing_time

    picking_time_list.append(Cn_1)
    packing_time_list.append(Cn_2)

    return picking_time_list, packing_time_list