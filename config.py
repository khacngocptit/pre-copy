from multiprocessing import cpu_count

N_JOBS = cpu_count()
SEED = 42

FOOD_DATABASE_PATH = 'data/danh_muc_thuc_pham.xlsx'
NUTRI_PATH = 'data/quy_dinh_dinh_duong.xlsx'
FOOD_DATABASE_OLD_PATH = "data/data_goc"
#
THOI_GIAN_CHAY = 60
NGUONG_DUOI_DINH_LUONG = 0.5
NGUONG_TREN_DINH_LUONG = 3
TY_LE_DIEU_CHINH_DINH_LUONG = 0.2
TY_LE_DIEU_CHINH_CALO_MON = 0.1
TY_LE_DIEU_CHINH_DON_GIA = 0.2
