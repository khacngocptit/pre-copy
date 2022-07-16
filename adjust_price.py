import numpy as np
from config import *


def cost(quantity, price):
    return np.sum(quantity * price) / 100


def adjust_price(first_price, best_chromo, input_data, food_data):
    cost_th = input_data['giaTien']
    if(input_data["type"]):
        best_quantity = best_chromo * food_data['Định lượng mẫu giáo gốc'].values
    else:
        best_quantity = best_chromo * food_data['Định lượng nhà trẻ gốc'].values

    best_price = first_price.copy().astype('float')
    for i in range(len(best_price)):
        if (c := cost(best_quantity, best_price)) == (t := cost_th[0]):
            break
        allele = abs(t - c) / best_quantity[i] * 100
        allele_th = best_price[i] * TY_LE_DIEU_CHINH_DON_GIA
        if c < t:
            if allele > allele_th:
                best_price[i] += allele_th
            else:
                best_price[i] += allele
        else:
            if allele > allele_th:
                best_price[i] -= allele_th
            else:
                best_price[i] -= allele
    return best_price
