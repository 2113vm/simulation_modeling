import random

import simpy
import numpy as np


"""
Вариант 8.

На станции техобслуживания автомобилей 4 рабочих выполняют два вида работ: 
шиномонтаж и балансировку. 
Причем каждую операцию выполняют два рабочих, но для шиномонтажа существуют два рабочих места. 
Поток автомобилей является пуассоновским со значением среднего интервала, равным 35 мин. 
80% автомобилей будут подвергаться и шиномонтажу и балансировки, 
а остальные — равновероятностно одной из операций. 
Время обслуживания автомобиля распределено экспоненциально со значением среднего, 
равным 45 мин для монтажа и 15 мин для балансировки. 
Если клиенты подъезжают и не застают свободного места для ожидания, они уезжают .

Необходимо решить, какое число мест на стоянке следует отвести для автомобилей, 
ожидающих обслуживания. 
Необходимо написать модель такой системы и использовать ее для исследования системы 
при использовании одного, двух, трех мест на стоянке. 
Определить оптимальное числа мест на стоянке. 
В каждом из этих случаев надо моделировать работу в течение восьмичасового рабочего дня
 и оценить долю клиентов, оставшихся без обслуживания
 """


def get_time_service(is_mount=True):
    return np.random.exponential(45) if is_mount else np.random.exponential(15)


def get_type_service():
    if random.random() < 0.8:
        return {'is_balancing': True, 'is_mounting': True}
    else:
        if random.random() < 0.5:
            return {'is_balancing': False, 'is_mounting': True}
        else:
            return {'is_balancing': True, 'is_mounting': False}


def car(env, res: list, start_time):
    global len_queue
    global max_len_queue
    global car_losses
    global car_complete
    m1, m2, b = res
    yield env.timeout(start_time)
    if not len_queue + 1 > max_len_queue:
        len_queue += 1
        services = get_type_service()
        is_bal, is_mount = services['is_balancing'], services['is_mounting']
        with m1.request() as m1_req, m2.request() as m2_req, b.request() as b_req:
            if is_bal and is_mount:
                yield (m1_req & b_req) | (m2_req & b_req)
                env.timeout(get_time_service(is_mount=True) + get_time_service(is_mount=False))
                len_queue -= 1
                car_complete += 1
            if is_bal and not is_mount:
                yield b_req
                env.timeout(get_time_service(is_mount=False))
                len_queue -= 1
                car_complete += 1
            if not is_bal and is_mount:
                yield m1_req | m2_req
                env.timeout(get_time_service(is_mount=True))
                len_queue -= 1
                car_complete += 1
    else:
        car_losses += 1


if __name__ == '__main__':

    # create environment
    env = simpy.Environment()
    mounting_1 = simpy.Resource(env=env, capacity=1)
    mounting_2 = simpy.Resource(env=env, capacity=1)
    balancing = simpy.Resource(env=env, capacity=1)

    # may be equal 1, 2 or 3
    max_len_queue = 1
    len_queue = 0

    car_losses = 0
    car_complete = 0

    sim_time = 8 * 60  # Время симуляции - 60 * 8 = 480 минут

    time_car = np.random.poisson(35, 100)
    filter_car = np.cumsum(time_car) < sim_time
    time_car = time_car[filter_car]

    for t in time_car:
        env.process(car(env, [mounting_1, mounting_2, balancing], t))

    env.run()
    print(f'Машин обслужено = {car_complete}, машин пропущено = {car_losses}')
