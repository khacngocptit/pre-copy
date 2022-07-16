import numpy as np
import pandas as pd
from numpy import random
from time import time
from config import *

random.seed(SEED)

N_POP = 100
MUTATE_RATE = 0.1


class Base:  # Genetic Algorithm
    def __init__(self, input_data, food_data,type_data, first_chromo, down_rate, up_rate):
        self.input_data = input_data
        self.food_data = food_data
        self.type_data = type_data
        self.first_chromo = first_chromo
        self.down_rate = down_rate
        self.up_rate = up_rate
        self.n_gene = len(down_rate)
        self.time = THOI_GIAN_CHAY / 2
        self.calo_df = pd.read_excel(NUTRI_PATH, sheet_name='Calo')
        self.nutri_df = pd.read_excel(NUTRI_PATH, sheet_name='Dinh duong')
        self.pop = self.init_pop()

    def init_pop(self):
        pop = [[self.first_chromo, self.evaluate(self.first_chromo)]]
        print("???",pop)
        for _ in range(N_POP-1):
            chromo = self.first_chromo.copy()
            for i in range(self.n_gene):
                if random.random() < 0.5:
                    chromo[i] = random.uniform(
                        self.down_rate[i], self.up_rate[i])
            fitness = self.evaluate(chromo)
            pop.append([chromo, fitness])
        return pop

    def evaluate(self, chromo):
        so_bua = len(self.input_data['Menu'])
        if(self.type_data):
            calo_ths = self.calo_df.loc[self.calo_df['Số bữa']
                                        == so_bua, 'MinMamNon':].values
            nutri_ths = self.nutri_df.loc[:, 'MinMamNon':].values
        else:
            calo_ths = self.calo_df.loc[self.calo_df['Số bữa']
                                        == so_bua, 'MinNhaTre':].values
            nutri_ths = self.nutri_df.loc[:, 'MinNhaTre':].values
        total_calo_ths = np.sum(calo_ths, axis=0)
        
        calo_rate = self.input_data['calo_rate']
        
        if(self.type_data):
            quantity = chromo * self.food_data['Định lượng mẫu giáo gốc'].values
        else:
            quantity = chromo * self.food_data['Định lượng nhà trẻ gốc'].values

        fitness = 0
        total_calo = 0
        total_nutri = np.ones(3)

        i = 0
        for foods, calo_th in zip(self.input_data['Menu'].values(), calo_ths):
            calo_each_meal = 0
            calo = {}
            for food in foods:
                n = self.input_data['n_ingredient'][food.get("name")]

                calo100 = self.food_data.loc[self.food_data['Tên món ăn']
                                             == food.get("name"), 'Calo/100G'].values
                tl_thai_bo = self.food_data.loc[self.food_data['Tên món ăn']
                                                == food.get("name"), 'Tỷ lệ thái bỏ'].values
                calo[food.get("name")] = np.sum(
                    calo100 * (quantity[i:i+n]/100*(100-tl_thai_bo)/100))
                calo_each_meal += calo[food.get("name")]

                protit100 = self.food_data.loc[self.food_data['Tên món ăn']
                                               == food.get("name"), 'Protit nhà trẻ'].values
                lipit100 = self.food_data.loc[self.food_data['Tên món ăn']
                                              == food.get("name"), 'Lipit nhà trẻ'].values
                gluxit100 = self.food_data.loc[self.food_data['Tên món ăn']
                                               == food.get("name"), 'Gluxit nhà trẻ'].values
                total_nutri[0] += np.sum(protit100 *
                                         (quantity[i:i+n]/100*(100-tl_thai_bo)/100)) * 4
                total_nutri[1] += np.sum(lipit100 *
                                         (quantity[i:i+n]/100*(100-tl_thai_bo)/100)) * 9
                total_nutri[2] += np.sum(gluxit100 *
                                         (quantity[i:i+n]/100*(100-tl_thai_bo)/100)) * 4
                i += n
            total_calo += calo_each_meal

            for food in foods:
                r = calo[food.get("name")] / calo_each_meal
                if r < (t := calo_rate[food.get("name")] - TY_LE_DIEU_CHINH_CALO_MON):
                    fitness -= 50 + abs(r - t)
                if r > (t := calo_rate[food.get("name")] + TY_LE_DIEU_CHINH_CALO_MON):
                    fitness -= 50 + abs(r - t)

            if calo_each_meal < (t := calo_th[0]):
                fitness -= 50 + abs(calo_each_meal - t) / t
            if calo_each_meal > (t := calo_th[1]):
                fitness -= 50 + abs(calo_each_meal - t) / t

        if total_calo < (t := total_calo_ths[0]):
            fitness -= 50 + abs(total_calo - t) / t
        if total_calo > (t := total_calo_ths[1]):
            fitness -= 50 + abs(total_calo - t) / t

        for nutri, nutri_th in zip(total_nutri, nutri_ths):
            r = nutri / total_calo
            if r < (t := nutri_th[0]):
                fitness -= 1 + abs(r - t)
            if r > (t := nutri_th[1]):
                fitness -= 1 + abs(r - t)

        return fitness

    def select(self):
        pop = np.array(self.pop, dtype='object')
        tournament = list(
            pop[np.random.choice(len(self.pop), 5, replace=False)])
        tournament = sorted(tournament, key=lambda x: x[1], reverse=True)
        return tournament[0], tournament[1]

    def crossover(self, parent1, parent2):
        offstring = []
        for i in range(self.n_gene):
            if np.random.uniform() < 0.5:
                offstring.append(parent1[0][i])
            else:
                offstring.append(parent2[0][i])
        offstring = np.array(offstring)
        fitness = self.evaluate(offstring)
        return (offstring, fitness)

    def mutate(self, chromo):
        mutated_chromo = chromo[0].copy()
        i = random.randint(self.n_gene)
        mutated_chromo[i] = random.uniform(self.down_rate[i], self.up_rate[i])
        fitness = self.evaluate(mutated_chromo)
        return (mutated_chromo, fitness)

    def replace(self):
        sorted_pop = sorted(self.pop, key=lambda x: x[1], reverse=True)
        new_pop = sorted_pop[:100]
        return new_pop

    def run(self):
        t = time()
        self.pop = self.replace()
        best_fitness = self.pop[0][1]
        while (e := int(time() - t)) < self.time:
            if self.pop[0][1] == 0:
                best_fitness = self.pop[0][1]
                print('\n\033[92m' + '[%4d/%4d] Found optimal chromosome.' %
                      (e, self.time), end='')
                break
            elif self.pop[0][1] > best_fitness:
                best_fitness = self.pop[0][1]
                print('[%4d/%4d] Best fitness: %.4f' %
                      (e, self.time, best_fitness), end='\r', flush=True)

            # Crossover
            parent1, parent2 = self.select()
            offstr1 = self.crossover(parent1, parent2)
            offstr2 = self.crossover(parent1, parent2)

            # Mutate
            if random.uniform() <= MUTATE_RATE:
                offstr1 = self.mutate(offstr1)
            if random.uniform() <= MUTATE_RATE:
                offstr2 = self.mutate(offstr2)

            self.pop.extend([offstr1, offstr2])
            self.pop = self.replace()

        print('\033[0m')
        best_chromo = self.pop[0][0]
        return best_chromo, best_fitness


class Core(Base):
    def __init__(self, input_data, food_data,type_data):
        self.n_gene = len(input_data['calo_rate'])
        print(len(input_data['calo_rate']))
        self.down_rate = [NGUONG_DUOI_DINH_LUONG] * self.n_gene
        self.up_rate = [NGUONG_TREN_DINH_LUONG] * self.n_gene
        # type_data = input_data["type"]
        self.first_chromo = self.init_chromo()
        super().__init__(input_data, food_data,type_data,
                         self.first_chromo, self.down_rate, self.up_rate)

    def init_chromo(self):
        first_chromo = []
        for i in range(self.n_gene):
            if self.down_rate[i] > 1:
                first_chromo.append(self.down_rate[i])
            else:
                first_chromo.append(1)
        return np.array(first_chromo, dtype='float')

    def chromo_to_fchromo(self, chromo):
        fchromo = []
        for gene, (_, n) in zip(chromo, self.input_data['n_ingredient'].items()):
            fchromo.extend([gene] * n)
        return np.array(fchromo)

    def evaluate(self, chromo):
        fchromo = self.chromo_to_fchromo(chromo)
        return super().evaluate(fchromo)

    def run(self):
        best_chromo, best_fitness = super().run()
        best_chromo = self.chromo_to_fchromo(best_chromo)
        if best_fitness:
            down_rate = best_chromo - TY_LE_DIEU_CHINH_DINH_LUONG
            up_rate = best_chromo + TY_LE_DIEU_CHINH_DINH_LUONG
            base = Base(
                self.input_data,
                self.food_data,
                self.type_data,
                best_chromo,
                down_rate,
                up_rate
            )
            best_chromo, best_fitness = base.run()
        return best_chromo, best_fitness
