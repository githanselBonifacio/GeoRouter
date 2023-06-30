from datetime import datetime
from typing import List

from fastapi import APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder


from core.appointment_genetic import AppointmentGenenetic
from models.appointment import json_to_appointment, Appointment

router = APIRouter()


@router.post("/appointment_with_slack", tags=["genetic"])
async def order_appointments_slack(request: Request):
    data = await request.json()
    #if request.get('mobile_available') is None:
     #   raise HTTPException(status_code=400, detail="attribute 'mobile_available' not found")

    #if request.get('origin') is None:
     #   raise HTTPException(status_code=400, detail="attribute 'origin' not found")

    #if request.get('appointments') is None:
     #   raise HTTPException(status_code=400, detail="attribute 'appointments' not found")

    mobile_available = data['mobile_available']
    appointments = json_to_appointment(data['appointments'])
    origin = Appointment(id_appointment="0",
                         latitude=data["origin"]["latitude"],
                         longitude=data["origin"]["longitude"],
                         duration=data["origin"]["duration"],
                         slack=data["origin"]["slack"],
                         date=datetime.timestamp(
                             datetime.strptime(data["origin"]["date"], "%d-%m-%Y %H:%M"))
                         )

    number_generations = 500
    slack_penalty = -10e6
    size_initial_population = 10
    number_parents_mating = 5

    gen = AppointmentGenenetic(
        origin=origin,
        appointments=appointments,
        slack_penalty=slack_penalty,
        number_generations=number_generations,
        number_parents_mating=number_parents_mating,
        size_initial_population=size_initial_population,
        number_mobiles=mobile_available
    )
    gen.run()
    print(f"se calcularon {len(gen.displacements)} desplazamientos")
    json_response = jsonable_encoder(gen.best_solution())
    return json_response

@router.get('/displacement')
async def calcule_displacement():
    pass