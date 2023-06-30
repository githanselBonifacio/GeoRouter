import copy
import random
from itertools import islice
from typing import List, Callable
import numpy as np
from models.appointment import Appointment, divide_list_appointments
from utils.operations import calculate_time, max_sum_list, swap_list_items, change_list_items, delete_elements


class AppointmentGenenetic:
    def __init__(self,
                 origin: Appointment,
                 appointments: List[Appointment],
                 number_mobiles: int,
                 number_generations=1000,
                 size_initial_population=20,
                 number_parents_mating=5,
                 slack_penalty=-10e6,
                 ):

        self.actual_results = {}
        self.displacements = []
        self.appointments = appointments
        self.origin = origin
        self.number_mobiles = number_mobiles
        self.number_generations = number_generations
        self.size_initial_population = size_initial_population
        self.slack_penalty = slack_penalty
        self.number_parents_mating = number_parents_mating
        self.actual_population = None

    def create_population(self) -> np.array:
        population_initial = []
        for _ in range(self.size_initial_population):
            population_initial.append(
                divide_list_appointments(
                    appointments=self.appointments,
                    origin=self.origin,
                    number_divisions=self.number_mobiles
                )
            )
        return np.array(population_initial, dtype=object)

    def check_travel_time(self, pos1, pos2):
        for dic in self.displacements:
            if dic["pos1"] == pos1 and dic["pos2"] == pos2:
                return dic["time"]
        return None

    def performance(self,
                    individual: List[List[Appointment]],
                    calculate_travel_time: Callable[[float, float, float, float], float]) \
            -> [List[List[Appointment]], List[List[float]]]:

        score_by_mobile = []
        appointments = []
        for group in individual:
            slack_between_appointment = []
            appointment = []
            for g in range(len(group)):
                appointment.append(group[g])
                if g == len(group) - 1:
                    break

                check_travel = self.check_travel_time(
                    group[g].id_appointment,
                    group[g+1].id_appointment
                )
                if check_travel is None:
                    travel_time = calculate_travel_time(
                        group[g].latitude, group[g].longitude, group[g + 1].latitude, group[g + 1].longitude)
                    self.displacements.append({
                        "pos1": group[g].id_appointment,
                        "pos2": group[g + 1].id_appointment,
                        "time": travel_time
                        })
                else:
                    travel_time = copy.deepcopy(check_travel)

                total_time = travel_time + group[g].duration
                accumulated_slack = group[g + 1].date - (group[g].date + total_time)
                if accumulated_slack < 0:
                    slack_between_appointment.append(-abs(accumulated_slack * self.slack_penalty))
                else:
                    slack_between_appointment.append(accumulated_slack)

            appointments.append(appointment)
            score_by_mobile.append(slack_between_appointment)
        return appointments, score_by_mobile

    @staticmethod
    def fitness(score_by_mobile: List[List[float]]) -> float:
        return sum(sum(s) for s in score_by_mobile)

    def calculate_population_fitness(self, func_calculate_time: Callable[[float, float, float, float], float]):
        for i in range(len(self.actual_population)):
            appointments, score_by_mobile = self.performance(self.actual_population[i], func_calculate_time)
            fitness_appointment = self.fitness(score_by_mobile)
            self.actual_results[i] = [fitness_appointment, appointments, score_by_mobile]

        results_sorted = dict(sorted(self.actual_results.items(), key=lambda x: x[1][0], reverse=True))
        self.actual_results = dict(islice(results_sorted.items(), self.number_parents_mating))

    def select_parents(self):
        results_appointment = np.array(list(self.actual_results.values())[:self.number_parents_mating], dtype=object)
        parents = []
        for sublist in results_appointment:
            parents.append(sublist[1])

        return np.array(parents, dtype=object)

    @staticmethod
    def find_coordinates_negative_slack(lst, ic=0):
        coordinates = []
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] < 0:
                    coordinates.append((i, j + ic))
        return [tupla for tupla in coordinates if tupla[-1] != 0]

    def mutate(self):
        results_appointment = np.array(list(self.actual_results.values())[:self.number_parents_mating], dtype=object)
        next_parents = []
        slacks_coor = []
        slack_population = []
        actual_population_g = []

        for sublist in results_appointment:
            corr = self.find_coordinates_negative_slack(sublist[2], ic=random.randint(0, 1))
            if len(corr) == 0:
                return np.empty(0)
            slacks_coor.append(corr)
            slack_population.append(sublist[2])
            actual_population_g.append(sublist[1])

        for i in range(len(actual_population_g)):
            count = random.random()
            pos1 = random.choice(slacks_coor[i])
            pos2 = (max_sum_list(slack_population[i]), -1)
            if count > 0.5:
                individual_next = swap_list_items(actual_population_g[i], pos1, pos2)
            else:
                individual_next = change_list_items(actual_population_g[i], pos1, pos2)

            next_parents.append(individual_next)

        for lista_appointments in next_parents[0]:
            lista_appointments.sort(key=lambda appointment: appointment.date)

        return np.array(next_parents, dtype=object)

    def run(self):
        self.actual_population = self.create_population()

        for g in range(self.number_generations):
            self.calculate_population_fitness(func_calculate_time=calculate_time)

            self.actual_population = self.select_parents()

            next_generation_parents = self.mutate()

            if len(next_generation_parents) == 0:
                print(f"Se realizaron {g} generaciones")
                break
            else:
                self.actual_population = next_generation_parents

    def best_solution(self):
        best_solution = {}
        last_results = copy.deepcopy(self.actual_results)
        key_max_slack = max(last_results, key=lambda k: last_results[k])
        best_order_appointments = last_results[key_max_slack]
        negative_slack_appointment_coordinates = self.find_coordinates_negative_slack(best_order_appointments[2], ic=1)
        scheduled, no_scheduled = delete_elements(best_order_appointments[1], negative_slack_appointment_coordinates)
        best_solution['scheduled'] = scheduled
        best_solution['no_scheduled'] = no_scheduled
        return best_solution
