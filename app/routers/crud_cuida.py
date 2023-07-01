import logging
from typing import List
from datetime import datetime
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from core.appointment_genetic import AppointmentGenenetic
from db.config_postgresql import engine
from models.appointment import json_to_appointment, Appointment
from routers.openrouter import calcular_tiempo_desplazamiento
from utils.operations import sum_date_secods

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
router = APIRouter()


@router.get("/proffesionales/{id_region}", tags=["crud"])
async def get_proffesionales_regions(id_region: int):
    with engine.connect() as conn:
        result = conn.execute(f"SELECT * from public.get_profesionales_regionales({id_region})")
        professionals = result.fetchall()
        if professionals is None:
            return {"error": "profesional not found"}
    return jsonable_encoder(professionals)


@router.get("/shift/", tags=["crud"])
async def get_turns_regions(date: str, id_region: int, id_schedule_shift: int):
    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT * from  public.get_turno_regional_horario('{date}', {id_region}, {id_schedule_shift})"
        )
        shifts = result.fetchall()
        if shifts is None:
            return {"error": "turno not found"}
    return jsonable_encoder(shifts)


@router.get("/regions", tags=["crud", "regional", "Listar"])
async def get_regions():
    with engine.connect() as conn:
        result = conn.execute(
            "SELECT * from public.regionales"
        )
        regionales = result.fetchall()
        if result is None:
            return {"error": "User not found"}
        return jsonable_encoder(regionales)


@router.get("/horario_turno", tags=["crud", "regional", "Listar"])
async def get_horario_turno():
    with engine.connect() as conn:
        result = conn.execute(
            "SELECT * from public.horario_turno"
        )
        horarios_turno = result.fetchall()
        if result is None:
            return {"error": "User not found"}
        return jsonable_encoder(horarios_turno)


@router.get("/citas", tags=["citas"])
async def get_citas_profesional(date: str, id_region: int, id_schedule_shift: int):
    with engine.connect() as conn:
        result_citas_atencion_profesional = conn.execute(f"SELECT * from public.get_profesionales_regionales('{id_region}')")
        if result_citas_atencion_profesional is None:
            return {"error": "profesional not found"}

        professionals = jsonable_encoder(result_citas_atencion_profesional.fetchall())
        for p in professionals:
            p['responsable'] = f"{p['primer_nombre']} {p['segundo_nombre']} {p['primer_apellido']} {p['segundo_apellido']}"
            del p["primer_nombre"]
            del p["segundo_nombre"]
            del p["primer_apellido"]
            del p["segundo_apellido"]

            result_citas_atencion = conn.execute(
                f"SELECT * from public.get_citas_profesional_asignado("
                f"'{date}',{id_region},{id_schedule_shift}, '{p['numero_identificacion']}');"
            )
            citas = result_citas_atencion.fetchall()
            cita_atencion_json = jsonable_encoder(citas)
            for c in cita_atencion_json:
                c['tipo'] = "visita"

            #desplazamientos
            result_citas_desplazamiento = conn.execute(
                f"SELECT * from public.get_desplazamientos_profesional_asignado("
                f"'{date}',{id_region},{id_schedule_shift}, '{p['numero_identificacion']}');"
            )
            desplazamientos = result_citas_desplazamiento.fetchall()
            desplazamientos_json = jsonable_encoder(desplazamientos)

            for d in desplazamientos_json:
                d['tipo'] = "Desplazamiento"
                d['id_cita'] = "desplazamiento a "+ d['id_cita_destino']
                del d['id_cita_partida']
                del d['id_cita_destino']
                d['identificacion_movil_tarea'] = d['id_movil']
                del d['id_movil']
                if len(str(d['conductor']).replace(" ", "")) == 0:
                    d['conductor'] = None

            citas_json = cita_atencion_json + desplazamientos_json

            p['citas'] = citas_json

        return sorted(professionals, key=lambda x: len(x["citas"]) == 0)


@router.get("/estado_cita/agendar")
async def asignar_profesional(id_cita: str, numero_identificacion: str, id_region: int):
    with engine.connect() as conn:
        conn.execute(
            f"UPDATE public.citas "
            f"SET id_profesional = '{numero_identificacion}',id_estado = 2 "
            f"WHERE public.citas.id = '{id_cita}' "
            f"and "
            f"(SELECT id from public.regionales WHERE public.regionales.id= {id_region}) = "
            f"(SELECT id_regional from public.ubicacion WHERE public.ubicacion.id = public.citas.id_ubicacion);"
        )
    return "se actualiza registro"


@router.get("/estado_cita/retirarProfesional")
async def desasignar_profesional(id_cita: str,  id_region: int):
    with engine.connect() as conn:
        conn.execute(
            f""
            f"UPDATE public.citas "
            f"SET id_profesional = NULL,id_estado = 1 "
            f"WHERE public.citas.id = '{id_cita}' "
            f"and "
            f"(SELECT id from public.regionales WHERE public.regionales.id= {id_region}) = "
            f"(SELECT id_regional from public.ubicacion WHERE public.ubicacion.id = public.citas.id_ubicacion);"
        )
    return "se actualiza registro"


@router.get("/estado_cita/desagendarTurno")
async def desagendar_turno_completo (fecha_turno:str):
    fecha = fecha_turno.replace("T", " ")[:-9]
    with engine.connect() as conn:
        conn.execute(
            f" UPDATE public.citas "
            f"SET id_profesional= NULL , id_estado = 1 "
            f"WHERE (public.citas.fecha_inicio BETWEEN CONCAT('{fecha}',' 00:00:00')::timestamp "
            f"AND CONCAT('{fecha}',' 23:59:59')::timestamp);")
    return "se ha desagendado todo"

@router.get("/citas/reprogramar")
async def reprogramar_hora_cita(id_cita:str, fecha_programada:str, nueva_hora: str):
    with engine.connect() as conn:
        conn.execute(
            "UPDATE "
            "citas "
            "SET "
            f"fecha_programada = '{fecha_programada} {nueva_hora}' "
            "WHERE "
            f" id = '{id_cita}';"
        )
    return "se actualiza registro"


def consultar_citas_para_desplazamientos(datos_turno_profesionales):

    desplazamientos_profesional_turno = []
    id_profesionales = []
    for c in datos_turno_profesionales:
        id_profesionales.append(c['id_profesional'])
        with engine.connect() as conn:
             conn.execute(
                f"DELETE FROM desplazamiento WHERE id_profesional= '{c['id_profesional']}';"
            )


    id_profesionales = list(set(id_profesionales))
    fecha_turno = datos_turno_profesionales[0]['fecha_turno']
    id_horario_turno = datos_turno_profesionales[0]['id_horario_turno']
    for p in id_profesionales:

        with engine.connect() as conn:
            result = conn.execute(
                f"SELECT * from public.get_ubicaciones_idcitas('{fecha_turno}','{p}',{id_horario_turno});"
            )

        consulta_ubicaciones_citas = jsonable_encoder(result.fetchall())
        registro_profesional = {}
        desplazamiento_profesional = []

        for i in range(len(consulta_ubicaciones_citas) - 1):
            desplazamiento = calcular_tiempo_desplazamiento(
                (consulta_ubicaciones_citas[i]["latitud"], consulta_ubicaciones_citas[i]["longitud"]),
                (consulta_ubicaciones_citas[i + 1]["latitud"], consulta_ubicaciones_citas[i + 1]["longitud"]))

            registro_desplazamiento = {}
            registro_desplazamiento['id_cita_partida'] = consulta_ubicaciones_citas[i]["id_cita"]
            registro_desplazamiento['duracion_seg_cita_partida'] = consulta_ubicaciones_citas[i]["duracion_seg"]
            registro_desplazamiento['id_cita_destino'] = str(consulta_ubicaciones_citas[i + 1]["id_cita"]).replace("T", " ")
            registro_desplazamiento['fecha_inicio_desplazamiento'] = str(consulta_ubicaciones_citas[i]["fecha_programada"]).replace("T", " ")
            registro_desplazamiento['duracion_seg'] = desplazamiento
            registro_desplazamiento['holgura_seg'] = 1200
            registro_desplazamiento['id_estado'] = 1
            desplazamiento_profesional.append(registro_desplazamiento)

        registro_profesional['id_profesional'] = str(p)
        registro_profesional['desplazamientos'] = desplazamiento_profesional

        desplazamientos_profesional_turno.append(registro_profesional)
    return jsonable_encoder(desplazamientos_profesional_turno)


@router.post("/citas/calcularDesplazamiento")
async def calcular_desplazamiento(datos_turno_profesionales:List[object]):
    desplazamientos_profesionales = consultar_citas_para_desplazamientos(datos_turno_profesionales)


    values = []
    if not (len(desplazamientos_profesionales) == 1 and desplazamientos_profesionales[0] == {}):
        for p in desplazamientos_profesionales:
            for d in p["desplazamientos"]:
                fecha_inicio_desplazamiento = sum_date_secods(d['fecha_inicio_desplazamiento'],
                                                                  d['duracion_seg_cita_partida'])

                values.append(
                    (
                        d['id_cita_partida'],
                        d['id_cita_destino'],
                        p['id_profesional'],
                        fecha_inicio_desplazamiento,
                        fecha_inicio_desplazamiento,
                        d['duracion_seg'],
                        600,
                        1
                    )
                )

        values_string = str(values).replace('[','').replace(']','')
        sql_query = f"INSERT INTO " \
                "public.desplazamiento " \
                "(id_cita_partida, id_cita_destino, id_profesional, fecha_inicio_desplazamiento, " \
                "fecha_programada_desplazamiento, duracion_seg, holgura_seg, id_estado) " \
                f"VALUES {values_string};"
    try:
        with engine.connect() as conn:
            conn.execute(sql_query)

        return desplazamientos_profesionales
    except Exception:
        return None


@router.post("/citas/autoagendar")
async def autoagendar_citas(datos_turno_profesionales:List[object]):
    #construccion de data para algoritmo genetico
    data = {}
    id_region = datos_turno_profesionales[0]['id_regional']
    fecha_turno = datos_turno_profesionales[0]['fecha_programada'].replace("T", " ")[:-9]
    #profesionales
    with engine.connect() as conn:
        result = conn.execute(
            f"SELECT numero_identificacion FROM public.profesionales WHERE id_regional = {id_region};")

    profesionales = result.fetchall()
    #citas
    appointments = []

    for d in datos_turno_profesionales:
       registro = {}
       registro["id_appointment"] = d["id_cita"]
       registro["latitude"]       = d["latitud"]
       registro["longitude"]      = d["longitud"]
       registro["duration"]       = d["duracion_seg"]
       registro["slack"]          = d["holgura_seg"]
       registro["date"]           = d["fecha_programada"].replace("T", " ")[:-3]
       appointments.append(registro)

    #ubicacion origen
    origin = Appointment(id_appointment="0",
                         latitude=11.001311083973969,
                         longitude=-74.81237704232935,
                         duration= 0,
                         slack=900,
                         date=datetime.timestamp(
                             datetime.strptime("2023-06-09 06:00", "%Y-%m-%d %H:%M"))
                         )

    data['mobile_available'] = len(profesionales)

    data['appointments'] = appointments
    appointments = json_to_appointment(data['appointments'])
    data_json = jsonable_encoder(data)
    #algoritmo genetico
    number_generations = 500
    slack_penalty = -10e6
    size_initial_population = 10
    number_parents_mating = 5

    gen = AppointmentGenenetic(
        origin =origin,
        appointments = appointments,
        slack_penalty=slack_penalty,
        number_generations=number_generations,
        number_parents_mating=number_parents_mating,
        size_initial_population=size_initial_population,
        number_mobiles= data_json['mobile_available']
    )
    gen.run()
    print(f"se calcularon {len(gen.displacements)} desplazamientos")
    json_response = jsonable_encoder(gen.best_solution())

    for i in range(len(profesionales)):
         for j in range(1, len(json_response['scheduled'][i])):
                #agendar
            with engine.connect() as conn:
                conn.execute(
                    f"UPDATE public.citas "
                    f"SET id_profesional = '{profesionales[i][0]}',id_estado = 2 "
                    f"WHERE public.citas.id = '{json_response['scheduled'][i][j]['id_appointment']}' "
                    f"and "
                    f"(SELECT id from public.regionales WHERE public.regionales.id= {id_region}) = "
                    f"(SELECT id_regional from public.ubicacion WHERE public.ubicacion.id = public.citas.id_ubicacion);"
                )
    return json_response
