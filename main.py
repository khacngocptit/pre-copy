from email import header
from numpy import unicode_
import pandas as pd
import sys
import json
from Core import Core
from config import *
from adjust_price import *
from utils import evaluate
import csv
import requests
food_df = pd.read_excel(FOOD_DATABASE_PATH)
anh_abc=0
class Adjuster:
    def __init__(self, input):
        self.input_data, self.food_data , self.type_data = self.prepare_input(input)
        self.core = Core(
            input_data=self.input_data,
            food_data=self.food_data,
            type_data = self.type_data 
          
        )

    def prepare_input(self, input):
        input_data = input
        food_data = pd.DataFrame()

        n_ingredient = {}
        calo_rate = {}
        # for _, foods in input_data['Menu'].items():
        #     for food, rate in foods.items():
        #         df = food_df.loc[food_df['Tên món ăn'] == food, :]
        #         food_data = pd.concat([food_data, df], ignore_index=True)
        #         n_ingredient[food] = len(df)
        #         calo_rate[food] = rate
        # input_data['n_ingredient'] = n_ingredient
        # input_data['calo_rate'] = calo_rate

        # return input_data, food_data
        for meal in input_data['Menu']:
            for food in input_data['Menu'][meal]:
                df = food_df.loc[food_df['Tên món ăn'] == food.get('name'),:]
                food_data = pd.concat([food_data, df], ignore_index=True)
                n_ingredient[food.get('name')] = len(df)
                calo_rate[food.get('name')] = food.get('weight')
        input_data['n_ingredient'] = n_ingredient
        input_data['calo_rate'] = calo_rate
        type_data = input_data['type']
        return input_data, food_data, type_data

    def prepare_output(self, first_chromo, best_chromo, first_price, best_price,type_data):
        report_input = evaluate(first_chromo, first_price,
                                self.input_data, self.food_data,self.type_data)
        report_best = evaluate(best_chromo, best_price,
                               self.input_data, self.food_data,self.type_data)
        while len(report_best) < len(report_input):
            report_best.append('')
        report = pd.DataFrame({
            'Original Menu': report_input,
            'Best Menu': report_best
        })
        if(type_data):
            columns = ['Tên món ăn', 'Thành phần món ăn',
                    'Định lượng mẫu giáo gốc', 'Đơn giá']
            self.food_data = self.food_data.loc[:, columns]
            best_quantity = best_chromo * \
                self.food_data['Định lượng mẫu giáo gốc'].values
        else:
            columns = ['Tên món ăn', 'Thành phần món ăn',
                    'Định lượng nhà trẻ gốc', 'Đơn giá']
            self.food_data = self.food_data.loc[:, columns]
            best_quantity = best_chromo * \
                self.food_data['Định lượng nhà trẻ gốc'].values
        self.food_data['Trọng số'] = best_chromo
        self.food_data['Định lượng điều chỉnh'] = best_quantity
        self.food_data['Đơn giá điều chỉnh'] = best_price
        return report

    def run(self):
        first_chromo = self.core.init_chromo()

        first_fitness = self.core.evaluate(first_chromo)

        first_chromo = self.core.chromo_to_fchromo(first_chromo)

        first_price = self.food_data['Đơn giá'].values

        print('Original fitness: ', round(first_fitness, 4))

    
        if first_fitness == 0:
            best_chromo = first_chromo
            print('Input quantity is satisfying!')
        else:
            best_chromo, _ = self.core.run()

        best_price = adjust_price(
            first_price, best_chromo, self.input_data, self.food_data)

        report = self.prepare_output(
            first_chromo, best_chromo, first_price, best_price,self.type_data)
        return self.food_data, report

# def output_data_api(path_file_in,path_file_csv):
#     data = open(path_file_csv)

def get_name_component(fullname):
  tokens = fullname.split("@@")
  ten_mon = "@@".join(tokens[:-1])
  don_vi = tokens[-1]
  return (ten_mon, don_vi)


def api_mam_non(input):
    for meal in input["Menu"]:
        for mon in input['Menu'][meal]:
            if mon.get('donViId',None) != None :
                mon['name'] = mon['name']+'@@'+mon['donViId']

    adjuster = Adjuster(input)
    menu, report = adjuster.run()
    input["result"]=[]

   
    for i in range(len(report["Best Menu"])):
        if(report["Best Menu"][i] != ""):
            input["result"].append(report["Best Menu"][i])
    del input["giaTien"]
    
    print("Ngoc",menu)
   
    d_ = {}
    if(input["type"]):
        for i, row in menu.iterrows():
            if row["Tên món ăn"] not in d_:
                d_[row["Tên món ăn"]] = {}
            d_[row["Tên món ăn"]][row["Thành phần món ăn"]] = {
                    "name": row["Thành phần món ăn"],
                    "Định lượng mẫu giáo gốc": row["Định lượng mẫu giáo gốc"],
                    "Đơn giá": row["Đơn giá"],
                    "Trọng số": row["Trọng số"],
                    "Định lượng điều chỉnh" : row["Định lượng điều chỉnh"],
                    "Đơn giá điều chỉnh": row["Đơn giá điều chỉnh"],
            }
        for meal in input["Menu"]:
            for food in input["Menu"][meal]:
            
                for tp in food["thanhPhanMonAn"]:
                    tp["dinhLuongGoc"] = d_[food.get("name")][tp.get("name")].get("Định lượng mẫu giáo gốc")
                    tp["donGiaGoc"] = d_[food.get("name")][tp.get("name")].get("Đơn giá")
                    tp["trongSo"] = d_[food.get("name")][tp.get("name")].get("Trọng số")
                    tp["dinhLuongDieuChinh"] = d_[food.get("name")][tp.get("name")].get("Định lượng điều chỉnh")
                    tp["donGiaDieuChinh"] = d_[food.get("name")][tp.get("name")].get("Đơn giá điều chỉnh")
                


    else:
        for i, row in menu.iterrows():
            if row["Tên món ăn"] not in d_:
                d_[row["Tên món ăn"]] = {}
            d_[row["Tên món ăn"]][row["Thành phần món ăn"]] = {
                    "name": row["Thành phần món ăn"],
                    "Định lượng nhà trẻ gốc": row["Định lượng nhà trẻ gốc"],
                    "Đơn giá": row["Đơn giá"],
                    "Trọng số": row["Trọng số"],
                    "Định lượng điều chỉnh" : row["Định lượng điều chỉnh"],
                    "Đơn giá điều chỉnh": row["Đơn giá điều chỉnh"],
            }
        for meal in input["Menu"]:
            for food in input["Menu"][meal]:
                print(food)
                for tp in food["thanhPhanMonAn"]:
                    tp["dinhLuongGoc"] = d_[food.get("name")][tp.get("name")].get("Định lượng nhà trẻ gốc")
                    tp["donGiaGoc"] = d_[food.get("name")][tp.get("name")].get("Đơn giá")
                    tp["trongSo"] = d_[food.get("name")][tp.get("name")].get("Trọng số")
                    tp["dinhLuongDieuChinh"] = d_[food.get("name")][tp.get("name")].get("Định lượng điều chỉnh")
                    tp["donGiaDieuChinh"] = d_[food.get("name")][tp.get("name")].get("Đơn giá điều chỉnh")
    del input["n_ingredient"]
    del input["calo_rate"]

    input[ "response"] = 200    
    for meal in input["Menu"]:
        for mon in input['Menu'][meal]:
            if mon.get('donViId',None) != None :
                mon['name'] = mon['name'].split("@@")[0]
                
    
    return input


def change_menu(data):
    food_df = pd.read_excel(FOOD_DATABASE_PATH)
    if (data.get("don_vi", None) == None):
        ten_mon_an = data.get("ten_mon_cu")
    else:
        ten_mon_an =data.get("ten_mon_cu") + "@@" +data.get("don_vi")
    
    print(ten_mon_an)
    list_index = food_df.loc[(food_df['Tên món ăn']==ten_mon_an)].index.tolist()  
    for index in list_index:
        food_df.drop(index= index, inplace = True )
    if (data.get("data").get("don_vi", None) == None):
        ten_mon_an_sua = data.get("data").get("ten_mon")
    else:
        ten_mon_an_sua =data.get("data").get("ten_mon") + "@@" +data.get("data").get("don_vi")
    
    vong_lap = len(data.get("data", None).get("thanhPhanMonAn", None))
    output= {'response':'incorrect data'}
    for i in range(vong_lap):
        if data.get("data", None).get("thanhPhanMonAn", None)[i].get("dinhLuongNhaTre", None) == None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("dinhLuongMauGiao", None)== None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("tyLeThai", None) == None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("donGia", None) == None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("protid", None)== None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("lipid", None)== None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("glucid", None)== None:
            return output
        elif data.get("data", None).get("thanhPhanMonAn", None)[i].get("calo", None)== None:
            return output
    for i in range(vong_lap):
        print(data.get("data", None).get("thanhPhanMonAn", None)[i].get("ten", None))
        thanh_phan_mon_an = data.get("data", None).get("thanhPhanMonAn", None)[i].get("ten", None)
        print(ten_mon_an_sua)
       
        data_input = {
                "Tên món ăn": ten_mon_an_sua,
                "Thành phần món ăn": thanh_phan_mon_an,
                "Loại thực phẩm":  data.get("data", None).get("thanhPhanMonAn", None)[i].get("loaiThucPham", None),
                "Định lượng nhà trẻ gốc":  data.get("data", None).get("thanhPhanMonAn", None)[i].get("dinhLuongNhaTre", None),
                "Định lượng mẫu giáo gốc":  data.get("data", None).get("thanhPhanMonAn", None)[i].get("dinhLuongMauGiao", None),
                "Tỷ lệ thái bỏ":  data.get("data", None).get("thanhPhanMonAn", None)[i].get("tyLeThai", None),
                "Đơn giá" :  data.get("data", None).get("thanhPhanMonAn", None)[i].get("donGia", None),
                "Protit nhà trẻ" :  data.get("data", None).get("thanhPhanMonAn", None)[i].get("protid", None),
                "Lipit nhà trẻ" :  data.get("data", None).get("thanhPhanMonAn", None)[i].get("lipid", None),
                "Gluxit nhà trẻ" : data.get("data", None).get("thanhPhanMonAn", None)[i].get("glucid", None),
                "Calo/100G" :  data.get("data", None).get("thanhPhanMonAn", None)[i].get("calo", None)

        }
        food_df = food_df.append(data_input, ignore_index = True)
        food_df.to_excel('data/danh_muc_thuc_pham.xlsx', index=None)
    output={'response': 200}

    return output

def delete_menu(data):
    food_df = pd.read_excel(FOOD_DATABASE_PATH)
    print(data)
    if (data.get("don_vi", None) == None):
        ten_mon_an = data.get("ten_mon")
    else:
        ten_mon_an = data.get("ten_mon") + "@@" + data.get("don_vi")
    print(ten_mon_an)
    list_index = food_df.loc[(food_df['Tên món ăn']==ten_mon_an)].index.tolist()  
    for index in list_index:
        food_df.drop(index= index, inplace = True )
    food_df.to_excel('data/danh_muc_thuc_pham.xlsx', index=None)
    output={'response': 200}
    return output
   


def add_menu(data):
    food_df = pd.read_excel(FOOD_DATABASE_PATH)
    # print(data)
    vong_lap = len(data.get("thanhPhanMonAn", None))
    output= {'response':'incorrect data'}
    for i in range(vong_lap):
        if data.get("thanhPhanMonAn", None)[i].get("dinhLuongNhaTre", None) == None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("dinhLuongMauGiao", None)== None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("tyLeThai", None) == None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("donGia", None) == None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("protid", None)== None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("lipid", None)== None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("glucid", None)== None:
            return output
        elif data.get("thanhPhanMonAn", None)[i].get("calo", None)== None:
            return output
    if (data.get("donViId", None) == None):
        ten_mon_an = data.get("name")
    else:
        ten_mon_an =data.get("name") + "@@" +data.get("donViId")
    # print(ten_mon_an)
    vong_lap = len(data.get("thanhPhanMonAn", None))
    for i in range(vong_lap):
        thanh_phan_mon_an = data.get("thanhPhanMonAn", None)[i].get("ten", None)
        # print(thanh_phan_mon_an)
       
        data_input = {
                "Tên món ăn": ten_mon_an,
                "Thành phần món ăn": thanh_phan_mon_an,
                "Loại thực phẩm": data.get("thanhPhanMonAn", None)[i].get("loaiThucPham", None),
                "Định lượng nhà trẻ gốc": data.get("thanhPhanMonAn", None)[i].get("dinhLuongNhaTre", None),
                "Định lượng mẫu giáo gốc": data.get("thanhPhanMonAn", None)[i].get("dinhLuongMauGiao", None),
                "Tỷ lệ thái bỏ": data.get("thanhPhanMonAn", None)[i].get("tyLeThai", None),
                "Đơn giá" : data.get("thanhPhanMonAn", None)[i].get("donGia", None),
                "Protit nhà trẻ" : data.get("thanhPhanMonAn", None)[i].get("protid", None),
                "Lipit nhà trẻ" : data.get("thanhPhanMonAn", None)[i].get("lipid", None),
                "Gluxit nhà trẻ" :data.get("thanhPhanMonAn", None)[i].get("glucid", None),
                "Calo/100G" : data.get("thanhPhanMonAn", None)[i].get("calo", None)

        }
                            
    # print(data_input)
        food_df = food_df.append(data_input, ignore_index = True)
        food_df.to_excel('data/danh_muc_thuc_pham.xlsx', index=None)
    output={'response': 200}
    return output


def tinh_toan_kho(input):

    # with open("./data/input.json", 'r', encoding='utf-8') as f:
    #     input = json.load(f)
    # anh_abc = anh_abc +1
    # print(anh_abc)
    adjuster = Adjuster(input)
    menu, report = adjuster.run()
    # print("2")
    input["result"]=[]

    for i in range(len(report["Best Menu"])):
        if(report["Best Menu"][i] != ""):
            input["result"].append(report["Best Menu"][i])
    del input["giaTien"]
    d_ = {}
    if(input["type"]):
        for i, row in menu.iterrows():
            if row["Tên món ăn"] not in d_:
                d_[row["Tên món ăn"]] = {}
            d_[row["Tên món ăn"]][row["Thành phần món ăn"]] = {
                    "name": row["Thành phần món ăn"],
                    "Định lượng mẫu giáo gốc": row["Định lượng mẫu giáo gốc"],
                    "Đơn giá": row["Đơn giá"],
                    "Trọng số": row["Trọng số"],
                    "Định lượng điều chỉnh" : row["Định lượng điều chỉnh"],
                    "Đơn giá điều chỉnh": row["Đơn giá điều chỉnh"],
            }
        for meal in input["Menu"]:
            for food in input["Menu"][meal]:
                food["thanhPhanMonAn"]=[]
                for thanh_phan in d_[food.get("name")]:
                    data_gui ={}
                    data_gui["name"]= food.get("name")
                    data_thanh_phan_mon_an ={}
                    data_thanh_phan_mon_an["name"] =d_[food.get("name")][thanh_phan].get("name")
                    data_gui["thanhPhanMonAn"] = data_thanh_phan_mon_an["name"]
                    data_thanh_phan_mon_an["dinhLuongGoc"] = d_[food.get("name")][thanh_phan].get("Định lượng mẫu giáo gốc")
                    data_thanh_phan_mon_an["donGiaGoc"] = d_[food.get("name")][thanh_phan].get("Đơn giá")
                    data_thanh_phan_mon_an["trongSo"] = d_[food.get("name")][thanh_phan].get("Trọng số")
                    data_thanh_phan_mon_an["dinhLuongDieuChinh"] = d_[food.get("name")][thanh_phan].get("Định lượng điều chỉnh")
                    data_thanh_phan_mon_an["donGiaDieuChinh"] = d_[food.get("name")][thanh_phan].get("Đơn giá điều chỉnh")
                    food["thanhPhanMonAn"].append(data_thanh_phan_mon_an)
                    print(data_gui)
    else:
        for i, row in menu.iterrows():
            if row["Tên món ăn"] not in d_:
                d_[row["Tên món ăn"]] = {}
            d_[row["Tên món ăn"]][row["Thành phần món ăn"]] = {
                    "Định lượng nhà trẻ gốc": row["Định lượng nhà trẻ gốc"],
                    "Đơn giá": row["Đơn giá"],
                    "Trọng số": row["Trọng số"],
                    "Định lượng điều chỉnh" : row["Định lượng điều chỉnh"],
                    "Đơn giá điều chỉnh": row["Đơn giá điều chỉnh"],
            }

        for meal in input["Menu"]:
            for food in input["Menu"][meal]:
                food["thanhPhanMonAn"]=[]
                for thanh_phan in d_[food.get("name")]:
                    data_thanh_phan_mon_an ={}
                    data_thanh_phan_mon_an["name"] =d_[food.get("name")][thanh_phan].get("name")
                    data_thanh_phan_mon_an["dinhLuongGoc"] =d_[food.get("name")][thanh_phan].get("Định lượng nhà trẻ gốc")
                    data_thanh_phan_mon_an["donGiaGoc"] = d_[food.get("name")][thanh_phan].get("Đơn giá")
                    data_thanh_phan_mon_an["trongSo"] = d_[food.get("name")][thanh_phan].get("Trọng số")
                    data_thanh_phan_mon_an["dinhLuongDieuChinh"] = d_[food.get("name")][thanh_phan].get("Định lượng điều chỉnh")
                    data_thanh_phan_mon_an["donGiaDieuChinh"] = d_[food.get("name")][thanh_phan].get("Đơn giá điều chỉnh")
                    food["thanhPhanMonAn"].append(data_thanh_phan_mon_an)

    del input["n_ingredient"]
    del input["calo_rate"]      
    # data = json.dumps(input,ensure_ascii=False)
    # # with open("./data/output.json", "w", encoding='utf-8') as json_file:
    # #     json_file.write(data)
    return input
def sua_thanh_phan_cua_mon_an(data):
    print("data in", data)
    food_df = pd.read_excel(FOOD_DATABASE_PATH)
    vong_lap = len(data.get("data_cu"))
    for i in range(vong_lap):
        if (data.get("data_cu", None)[i].get("don_vi") == None):
            ten_mon_an = data.get("data_cu", None)[i].get("ten_mon_cu")
        else:
            ten_mon_an =data.get("data_cu", None)[i].get("ten_mon_cu") + "@@" +data.get("data_cu", None)[i].get("don_vi")
        
      
        list_index = food_df.loc[(food_df['Tên món ăn']==ten_mon_an)].index.tolist()     
        for index in list_index:
            food_df.drop(index= index, inplace = True )
    food_df.to_excel('data/danh_muc_thuc_pham.xlsx', index=None)
    food_df = pd.read_excel(FOOD_DATABASE_PATH)
    print(list_index)
    vong_lap_1 = len(data.get("data", None))
    for j in range(vong_lap_1):
        vong_lap = len(data.get("data", None)[j].get("thanhPhanMonAn", None))
        output= {'response':'incorrect data'}
        for i in range(vong_lap):
            if data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("dinhLuongNhaTre", None) == None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("dinhLuongMauGiao", None)== None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("tyLeThai", None) == None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("donGia", None) == None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("protid", None)== None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("lipid", None)== None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("glucid", None)== None:
                return output
            elif data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("calo", None) == None:
                return output

    if(data.get("data", None) != None):
        vong_lap_1 = len(data.get("data", None))
        
        for j in range(vong_lap_1):
            if (data.get("data")[i].get("don_vi", None) == None):
                ten_mon_an_sua = data.get("data", None)[j].get("ten_mon")
            else:
                ten_mon_an_sua =data.get("data", None)[j].get("ten_mon") + "@@" +data.get("data")[j].get("don_vi")
        
            vong_lap = len(data.get("data", None)[j].get("thanhPhanMonAn", None))
            for i in range(vong_lap):
                print(i)
                print(data.get("data")[j])
                thanh_phan_mon_an = data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("ten", None)
                
            
                data_input = {
                        "Tên món ăn": ten_mon_an_sua,
                        "Thành phần món ăn": thanh_phan_mon_an,
                        "Loại thực phẩm":  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("loaiThucPham", None),
                        "Định lượng nhà trẻ gốc":  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("dinhLuongNhaTre", None),
                        "Định lượng mẫu giáo gốc":  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("dinhLuongMauGiao", None),
                        "Tỷ lệ thái bỏ":  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("tyLeThai", None),
                        "Đơn giá" :  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("donGia", None),
                        "Protit nhà trẻ" :  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("protid", None),
                        "Lipit nhà trẻ" :  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("lipid", None),
                        "Gluxit nhà trẻ" : data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("glucid", None),
                        "Calo/100G" :  data.get("data", None)[j].get("thanhPhanMonAn", None)[i].get("calo", None)

                }
                food_df = food_df.append(data_input, ignore_index = True)
                food_df.to_excel('data/danh_muc_thuc_pham.xlsx', index=None)
        output={'response': 200}

        return output
    else: 
        output={"status":"detele"}
        return output   