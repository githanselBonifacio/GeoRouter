import random
from datetime import datetime, timedelta
from typing import List, Any, Union

from pydantic import BaseModel, Field

from utils.operations import find_addends


class Appointment:
    id_appointment: str
    latitude: float
    longitude: float
    duration: int
    slack: int
    date: Union[float, str]

    def __init__(self,
                 id_appointment: str,
                 latitude: float,
                 longitude: float,
                 duration: int,
                 slack: int,
                 date: Union[float, str]):
        """
        :param id_appointment: unique number that identifies the appointment
        :param latitude: latitude value of the place of appointment
        :param longitude: longitude value of the place of appointment
        :param slack: maximum slack of attention to the appointment (seconds)
        :param date: appointment date
        :param duration: appointment duration (seconds)
        """

        self.id_appointment = id_appointment
        self.latitude = latitude
        self.longitude = longitude
        self.slack = slack
        self.date = date
        self.duration = duration

    def __str__(self):
        return f"{self.id_appointment}, latitude={self.latitude}, " \
               f"longitude={self.longitude}, slack={self.slack}, date={self.date}, duration={self.duration})"

    def __repr__(self):
        return f"{self.id_appointment}"

    @staticmethod
    def create_default_list_appointment():
        """
        creates a list of citations randomly grouped into 4 sublists.
        :return: List[List[Appointment]]
        """
        tomorrow = datetime.utcnow() + timedelta(days=1)

        str_tomorrow = f"{tomorrow.day}-{tomorrow.month}-{tomorrow.year}"
        format_date = "%d-%m-%Y %H:%M"
        appointments = [Appointment("1", 10.998867, -74.827570, 1800, 900,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 08:00", format_date))),
                        Appointment("2", 11.004831, -74.816292, 3600, 3600,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 10:15", format_date))),
                        Appointment("3", 11.001397, -74.826874, 900, 27000,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 9:30", format_date))),
                        Appointment("4", 10.993486, -74.820135, 1200, 900,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 11:00", format_date))),
                        Appointment("5", 10.977166, -74.816718, 4200, 1800,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 08:30", format_date))),
                        Appointment("6", 10.972345, -74.807658, 4500, 900,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 10:45", format_date))),
                        Appointment("7", 10.970669, -74.810724, 5200, 1800,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 12:30", format_date))),
                        Appointment("8", 10.968626, -74.804684, 3600, 900,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 08:15", format_date))),
                        Appointment("9", 10.966256, -74.810394, 1800, 5500,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 10:30", format_date))),
                        Appointment("10", 10.965350, -74.817936, 7200, 900,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 11:40", format_date))),
                        Appointment("11", 10.989135, -74.808344, 4800, 2200,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 12:00", format_date))),
                        Appointment("12", 10.988777, -74.814695, 2700, 900,
                                    datetime.timestamp(
                                        datetime.strptime(str(str_tomorrow) + " 11:50", format_date)))]

        return appointments


def divide_list_appointments(appointments: List[Appointment], number_divisions: int, origin: Appointment):
    """
    :param origin:
    :param number_divisions:
    :type appointments: object with appointment attributes
    """
    sizes = find_addends(len(appointments), number_divisions)
    random.shuffle(appointments)
    if sum(sizes) != len(appointments):
        raise ValueError("Sum of sizes must equal length of list.")
    grouped_appointments = []
    start = 0
    for size in sizes:
        end = start + size
        grouped_appointments.append(appointments[start:end])
        start = end

    for lista_appointments in grouped_appointments:
        lista_appointments.append(origin)
        lista_appointments.sort(key=lambda appointment: appointment.date)

    return grouped_appointments


def json_to_appointment(json):
    appointments = []
    for a in json:
        appointment = Appointment(a['id_appointment'],
                                  a['latitude'],
                                  a['longitude'],
                                  a['duration'],
                                  a['slack'],
                                  datetime.timestamp(
                                      datetime.strptime(a['date'], "%Y-%m-%d %H:%M"))
                                  )

        appointments.append(appointment)
    return appointments
