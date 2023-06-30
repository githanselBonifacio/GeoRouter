import copy
import random
from typing import List
import numpy as np
from datetime import datetime, timedelta

def find_addends(number: int, number_addends: int) -> List[int]:
    addends = []
    sum_addends = 0
    for i in range(number_addends):
        if i < number_addends - 1:
            limit = number - number_addends - sum_addends
            if limit <= 0:
                limit = 1

            counter = random.randint(1, limit)
        else:
            counter = number - sum_addends
        addends.append(counter)
        sum_addends = sum_addends + counter
    return addends


def calculate_time(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    velocity_averange = 10
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radio de la Tierra en km
    return round((c * r) * 3600 / velocity_averange, 3)*2


def max_sum_list(lst):
    if len(lst) == 1:
        return lst[0]
    else:
        return lst.index(max(lst, key=sum))


def count_consecutives(lista):
    cont = 0
    for i in range(1, len(lista)):
        if lista[i][1] == lista[i - 1][1] + 1:
            cont += 1
    return cont


def swap_list_items(lst, pos1, pos2):
    list_c = copy.deepcopy(lst)
    val1 = list_c[pos1[0]][pos1[1]]
    val2 = list_c[pos2[0]][pos2[1]]
    list_c[pos1[0]][pos1[1]] = val2
    list_c[pos2[0]][pos2[1]] = val1
    return list_c


def change_list_items(lst, pos1, pos2):
    list_c = copy.deepcopy(lst)
    val1 = list_c[pos1[0]][pos1[1]]
    list_c[pos2[0]].append(val1)
    list_c[pos1[0]].pop(pos1[1])
    return list_c


def delete_elements(lst_d, index):
    lst = copy.deepcopy(lst_d)
    deleted = []
    new_lst = []
    for i, sublist in enumerate(lst):
        new_sublista = []
        for j, element in enumerate(sublist):
            if (i, j) in index:
                deleted.append(element)
            else:
                new_sublista.append(element)
        new_lst.append(new_sublista)
    return new_lst, deleted


def add_attributeJson(obj):
    obj['new_attribute'] = 'new_value'
    return obj


def sum_date_secods(fecha_str, duracion):

    fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
    nueva_fecha = fecha + timedelta(seconds=duracion)
    return  nueva_fecha.strftime('%Y-%m-%d %H:%M:%S')