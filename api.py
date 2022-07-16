from re import T
from fastapi import FastAPI, File, UploadFile,status,HTTPException, Query
import pandas as pd
import os ,sys , glob
from utils import process_data
from starlette.responses import FileResponse
from main import api_mam_non, change_menu, delete_menu, add_menu, tinh_toan_kho, sua_thanh_phan_cua_mon_an
import json,codecs
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
from config import *
from os import walk
app = FastAPI()

@app.post("/uploadfile/menu")
async def create_upload_file_menu(uploaded_file: UploadFile = File(...)):
    FOOD_DATABASE_PATH = f"./data/danh_muc_thuc_pham.xlsx"
    data = pd.read_excel(FOOD_DATABASE_PATH)
    with open(FOOD_DATABASE_PATH, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    process_data(FOOD_DATABASE_PATH,data)
    return FileResponse(FOOD_DATABASE_PATH, media_type='application/octet-stream',filename="danh_muc_thuc_pham.xlsx")

@app.get("/get/file")
async def get_menu(file_location,file_name):
    return FileResponse(file_location, media_type='application/octet-stream',filename=file_name)

@app.post("/uploadfile/quy-dinh")
async def create_upload_file_quy_dinh(uploaded_file: UploadFile = File(...)):
    NUTRI_PATH = f"./data/quy_dinh_dinh_duong.xlsx"
    # with open(NUTRI_PATH, "wb+") as file_object:
    #     file_object.write(uploaded_file.file.read())
    return FileResponse(NUTRI_PATH, media_type='application/octet-stream',filename="quy_dinh_dinh_duong.xlsx")

@app.post("/uploadfile/chinh-menu",status_code=200)
async def create_upload_file_menu(input):
    # api_mam_non(data)
    try :
        data = json.loads(jsonable_encoder(input))
        return JSONResponse(status_code=status.HTTP_200_OK, content=api_mam_non(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Item not found")


@app.post("/uploadfile/show-menu",status_code=200)
async def show_menu(theLoai,soBua,giaTien,soLuongMenu:int, mon_an ):
    # api_mam_non(data)
    try :
        data_list_menu = []
        i = 0
        output_menu = "./Menu/"+theLoai+"/"+soBua+"/"+giaTien
   
        # print(output_menu)
        # for filename in glob.glob(os.path.join(output_menu, '*.json')):
        #     with open(filename, "r+", 'utf-8') as f:
        # for (dirpath, dirnames, filenames) in walk(output_menu):
        #     print(1)
        #     f.extend(filenames)
            # data_f = codecs.open(output_menu + f, "r+", 'utf-8')
            # data = json.load(data_f)
            # print(2)
            # print(type(text))
            # if key in data :
            #     i = i+1
            #     data_list_menu.append(data)
            # if i == soLuongMenu:
            #     return JSONResponse(status_code=status.HTTP_200_OK, content=data_list_menu)
            # break
        listOfFile = os.listdir(output_menu)
        allFiles = list()
        for entry in listOfFile:
        # Create full path
            fullPath = os.path.join(output_menu, entry)
        # # If entry is a directory then get the list of files in this directory 

            allFiles.append(fullPath)
        for f in allFiles  :
            data_f = codecs.open(f, "r+", 'utf-8')
            data = json.load(data_f)
            data_str = json.dumps(data, ensure_ascii=False).encode('utf8')
            data_str=data_str.decode('utf-8')
            # print(type(data_str))
            if data_str.find(mon_an) > -1 :
                
                i = i+1
                data_list_menu.append(data)
            if i == soLuongMenu:
                return JSONResponse(status_code=status.HTTP_200_OK, content=data_list_menu)

        return JSONResponse(status_code=status.HTTP_200_OK, content=data_list_menu)

    except ValueError:
        raise HTTPException(status_code=500, detail="Item not found")

@app.post("/menu/sua-thanh-phan-mon-an",status_code=200)
async def sua_thanh_phan_mon_an(input):
    try :
        print(1)
        data = json.loads(jsonable_encoder(input))
        print(23)
        return JSONResponse(status_code=status.HTTP_200_OK, content=change_menu(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Can not read data")

@app.post("/menu/them-thanh-phan-mon-an",status_code=200)
async def them_thanh_phan_mon_an(input):
    # api_mam_non(data)
    try :
        data = json.loads(jsonable_encoder(input))
        return JSONResponse(status_code=status.HTTP_200_OK, content=add_menu(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Item not found")

@app.post("/menu/xoa-thanh-phan-mon-an",status_code=200)
async def xoa_thanh_phan_mon_an(input):
    try :
        data = json.loads(jsonable_encoder(input))
        return JSONResponse(status_code=status.HTTP_200_OK, content=delete_menu(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Item not found")

@app.post("/menu/gen_menu",status_code=200)
async def gen_menu(input):
    try :
        data = json.loads(jsonable_encoder(input))
        return JSONResponse(status_code=status.HTTP_200_OK, content=gen_menu(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Time limit")

@app.post("/menu/tinh_toan_kho",status_code=200)
async def tinh_toan_kho_menu(input):
    try :
        data = json.loads(input)
        return JSONResponse(status_code=status.HTTP_200_OK, content=tinh_toan_kho(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Item not found")

@app.post("/menu/sua-thanh-phan-cua-mon-an",status_code=200)
async def sua_thanh_phan_mon_an(input):
    try :
      
        data = json.loads(jsonable_encoder(input))
        print(data)
        return JSONResponse(status_code=status.HTTP_200_OK, content=sua_thanh_phan_cua_mon_an(data))

    except ValueError:
        raise HTTPException(status_code=500, detail="Can not read data")