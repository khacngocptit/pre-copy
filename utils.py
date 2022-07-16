from unittest import result
import numpy as np
import pandas as pd
from config import *
from adjust_price import cost


calo_df = pd.read_excel(NUTRI_PATH, sheet_name='Calo')
nutri_df = pd.read_excel(NUTRI_PATH, sheet_name='Dinh duong')
columns = [
    'Tên món ăn',
    "Loại món ăn 1",
    "Loại món ăn 2",
    "Loại món ăn 3",
    'Thành phần món ăn',
    'Loại thực phẩm',
    'Định lượng nhà trẻ gốc',
    'Định lượng mẫu giáo gốc',
    'Tỷ lệ thái bỏ',
    'Đơn giá',
    'Protit nhà trẻ',
    'Lipit nhà trẻ',
    'Gluxit nhà trẻ',
    'Calo/100G'
]


def process_data(f,data):
    food_df = pd.read_excel(
        f, sheet_name='File goc')
    food_df = food_df.iloc[3:5284, [1, 2, 4, 6, 8, 9, 10, 12, 15, 16, 19, 20, 21, 22]]
    mapping = dict(zip(food_df.columns, columns))
    food_df.rename(columns=mapping, inplace=True)
    
    print(data)
    food_df
    food_name = []
    loai_mon_an_1 =[]
    loai_mon_an_2 =[]
    loai_mon_an_3 =[]
    prev_name = ""
    for name in food_df['Tên món ăn'].values:
        # print(name)
        if isinstance(name, str):
            prev_name = name
        food_name.append(prev_name)
    food_df['Tên món ăn'] = food_name


    prev_name = ""
    i=0
    for name in food_df['Loại món ăn 1'].values:
        if i > 0:
            if food_name[i] != food_name[i-1]:
                if isinstance(name, str):
                    prev_name = name
                else:
                    prev_name = ""
        else:
            if isinstance(name, str):
                prev_name = name
        loai_mon_an_1.append(prev_name)
        i = i+1
    food_df['Loại món ăn 1'] = loai_mon_an_1

    
    
    prev_name = ""
    i=0
    for name in food_df['Loại món ăn 2'].values:
        if i > 0:
            if food_name[i] != food_name[i-1]:
                if isinstance(name, str):
                    prev_name = name
                else:
                    prev_name = ""
        else:
            if isinstance(name, str):
                prev_name = name
        loai_mon_an_2.append(prev_name)
        i = i+1
    food_df['Loại món ăn 2'] = loai_mon_an_2

    prev_name = ""
    i=0
    for name in food_df['Loại món ăn 3'].values:
        if i > 0:
            if food_name[i] != food_name[i-1]:
                if isinstance(name, str):
                    prev_name = name
                else:
                    prev_name = ""
        else:
            if isinstance(name, str):
                prev_name = name
        loai_mon_an_3.append(prev_name)
        i = i+1
    
    food_df['Loại món ăn 3'] = loai_mon_an_3
    print(type(food_df))


    food_df.dropna(subset=['Thành phần món ăn'],inplace=True)
    # food_df_old = pd.read_excel(FOOD_DATABASE_PATH)
    data_food = [food_df,data]
    # print(000000000000000000000000000000000000)
    # print(food_df)
    # print(000000000000000000000000000000000000)
    # print(food_df_old)
    # food_df.to_excel('data/danh_muc_thuc_pham1.xlsx', index=None)
    print(food_df)
    
    result = pd.concat(data_food)
    result.to_excel('data/danh_muc_thuc_pham.xlsx', index=None)

def evaluate(chromo, price, input_data, food_data,type_data):
    report = []
    so_bua = len(input_data['Menu'])

    if(type_data):
        calo_ths = calo_df.loc[calo_df['Số bữa']
                           == so_bua, 'MinMamNon':].values

        nutri_ths = nutri_df.loc[:, 'MinMamNon':].values
    else:
        calo_ths = calo_df.loc[calo_df['Số bữa']
                           == so_bua, 'MinNhaTre':].values

        nutri_ths = nutri_df.loc[:, 'MinNhaTre':].values
    total_calo_ths = np.sum(calo_ths, axis=0)

    calo_rate = input_data['calo_rate']
    
    if(type_data):
        quantity = chromo * food_data['Định lượng mẫu giáo gốc'].values
    else: 
        quantity = chromo * food_data['Định lượng nhà trẻ gốc'].values
    total_cost = cost(quantity, price)
    cost_th = input_data['giaTien']


    fitness = 0
    total_calo = 0
    total_nutri = np.ones(3)

    i = 0
    for (meal, foods), calo_th in zip(input_data['Menu'].items(), calo_ths):
        calo_each_meal = 0
        calo = {}
        for food in foods:
            n = input_data['n_ingredient'][food.get("name")]

            calo100 = food_data.loc[food_data['Tên món ăn']
                                    == food.get("name"), 'Calo/100G'].values
            tl_thai_bo = food_data.loc[food_data['Tên món ăn']
                                       == food.get("name"), 'Tỷ lệ thái bỏ'].values
            calo[food.get("name")] = np.sum(
                calo100 * (quantity[i:i+n]/100*(100-tl_thai_bo)/100))
            calo_each_meal += calo[food.get("name")]

            protit100 = food_data.loc[food_data['Tên món ăn']
                                      == food.get("name"), 'Protit nhà trẻ'].values
            lipit100 = food_data.loc[food_data['Tên món ăn']
                                     == food.get("name"), 'Lipit nhà trẻ'].values
            gluxit100 = food_data.loc[food_data['Tên món ăn']
                                      == food.get("name"), 'Gluxit nhà trẻ'].values
            total_nutri[0] += np.sum(protit100 *
                                     (quantity[i:i+n]/100*(100-tl_thai_bo)/100)) * 4
            total_nutri[1] += np.sum(lipit100 *
                                     (quantity[i:i+n]/100*(100-tl_thai_bo)/100)) * 9
            total_nutri[2] += np.sum(gluxit100 *
                                     (quantity[i:i+n]/100*(100-tl_thai_bo)/100)) * 4
            i += n
        total_calo += calo_each_meal

        # for food in foods:
        #     r = calo[food.get("name")] / calo_each_meal
        #     if r < (t := calo_rate[food.get("name")] - 0.1):
        #         fitness -= 10 + abs(r - t)
        #         report.append(
        #             f'Bữa {meal}: Tỷ lệ Calo THẤP ({round(r, 4)} < {round(t, 4)}), {food.get("name")}')
        #     if r > (t := calo_rate[food.get("name")] + 0.1):
        #         fitness -= 10 + abs(r - t)
        #         report.append(
        #             f'Bữa {meal}: Tỷ lệ Calo CAO ({round(r, 4)} > {round(t, 4)}), {food.get("name")}')
            
        if calo_each_meal < (t := calo_th[0]):
            fitness -= 10 + abs(calo_each_meal - t) / t
            report.append(
                f'Bữa {meal}: Hàm lượng Calo THẤP ({round(calo_each_meal, 2)} < {round(t, 2)})')
        if calo_each_meal > (t := calo_th[1]):
            report.append(
                f'Bữa {meal}: Hàm lượng Calo CAO ({round(calo_each_meal, 2)} > {round(t, 2)})')

    if total_calo < (t := total_calo_ths[0]):
        fitness -= 1 + abs(total_calo - t) / t
        report.append(
            f'Tổng hàm lượng Calo cả ngày THẤP ({round(total_calo, 2)} < {round(t, 2)})')
    if total_calo > (t := total_calo_ths[1]):
        fitness -= 1 + abs(total_calo - t) / t
        report.append(
            f'Tổng hàm lượng Calo cả ngày CAO ({round(total_calo, 2)} > {round(t, 2)})')
    report.append(
        f'Thành tiền: {total_cost} ({evaluate_cost(total_cost, cost_th)})')
    for nutri, nutri_th, nutri_name in zip(total_nutri, nutri_ths, nutri_df['Chất dinh dưỡng'].values):
        r = nutri / total_calo
        print(nutri_name)
        if r < (t := nutri_th[0]):
            fitness -= 1 + abs(r - t)
            report.append(
                f'Tỷ lệ {nutri_name} THẤP ({round(r, 4)} < {round(t, 4)})')
        if r > (t := nutri_th[1]):
            fitness -= 1 + abs(r - t)
            report.append(
                f'Tỷ lệ {nutri_name} CAO ({round(r, 4)} > {round(t, 4)})')

    return report


def evaluate_cost(cost, cost_th):
    if cost < cost_th[0]:
        return 'THẤP'
    elif cost > cost_th[1]:
        return 'CAO'
    else:
        return 'OK'
