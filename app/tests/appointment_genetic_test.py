import unittest
from datetime import datetime, timedelta
from core.appointment_genetic import AppointmentGenenetic
from models.appointment import Appointment
from utils.operations import calculate_time


class AppointmentTest(unittest.TestCase):
    def find_coordinates_negative_slack_test(self):
        slack = [[0, 45664, -54554, 655, -4565],
                 [0, -4566, 545],
                 [0, 45568, 8789, 9877, -784564],
                 [0, -5454, -4566, 888546, 6545]]

        self.assertEqual(AppointmentGenenetic.find_coordinates_negative_slack(slack),
                         [(0, 2), (0, 4),
                          (1, 1),
                          (2, 4),
                          (3, 1), (3, 2)])

        self.assertEqual(AppointmentGenenetic.find_coordinates_negative_slack(slack, ic=1),
                         [(0, 3), (0, 5),
                          (1, 2),
                          (2, 5),
                          (3, 2), (3, 3)])

    def performance_test(self):
        score_expected = [
            [2995.0339999198914, 5796.621000051498, -67379449999.33243],
            [13962.90499997139, -108669489998.81744, 3495.0209999084473],
            [18571.673000097275, -207510580000.87738, 4256.371000051498],
            [15343.990999937057, -70240190000.53406, -56499809999.46594]]

        tomorrow = datetime.utcnow() + timedelta(days=1)
        str_tomorrow = f"{tomorrow.day}-{tomorrow.month}-{tomorrow.year} 07:00"
        origin_location = Appointment(0, 11.001311083973969, -74.81237704232935, 0, 900,
                                      datetime.timestamp(datetime.strptime(str_tomorrow.strip(), "%d-%m-%Y %H:%M")))

        gen = AppointmentGenenetic(
            origin=origin_location,
            appointments=Appointment.create_default_list_appointment(),
            slack_penalty=-10e6,
            number_generations=1,
            number_parents_mating=1,
            size_initial_population=1,
            number_mobiles=4
        )
        gen.actual_population = [gen.appointments[i:i + 3] for i in range(0, len(gen.appointments), 3)]
        gen.actual_population = [[origin_location] + sublist for sublist in gen.actual_population]

        _, score_by_mobile = gen.performance(gen.actual_population, calculate_time)

        self.assertEqual(score_by_mobile, score_expected)


if __name__ == '__main__':
    unittest.main()
