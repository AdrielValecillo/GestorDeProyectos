from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models import Propuesta, Alternativa, Argumentacion


def guardar_propuesta(db: Session, propuesta: str, alternativas: str):
    nueva_propuesta = Propuesta(descripcion=propuesta, alternativas_ia=alternativas)
    db.add(nueva_propuesta)
    db.commit()
    db.refresh(nueva_propuesta)
    return nueva_propuesta

def obtener_propuesta(db: Session, id_proyecto: int):
    return db.query(Propuesta).filter(Propuesta.id_proyecto == id_proyecto).first()

def obtener_ultima_propuesta(db: Session):
    return db.query(Propuesta).order_by(Propuesta.id_proyecto.desc()).first()

def guardar_alternativa(db: Session, id_proyecto: int, nombre: str, costo: int, eficiencia: int, facilidad: int, tiempo: int):
    nueva_alternativa = Alternativa(id_proyecto=id_proyecto, 
                                    nombre_alternativa=nombre, costo=costo, eficiencia=eficiencia, 
                                    facilidad_implementacion=facilidad, tiempo=tiempo)
    db.add(nueva_alternativa)
    db.commit()
    db.refresh(nueva_alternativa)
    return nueva_alternativa

def obtener_ulima_alternativa(db: Session):
    return db.query(Alternativa).order_by(Alternativa.id_alternativa.desc()).first()


def guardar_argumentacion(db: Session, id_alternativa: int, argumento: str, costo: str, eficiencia: str, facilidad: str, tiempo: str):
    nueva_argumentacion = Argumentacion(id_alternativa=id_alternativa, argumento=argumento, 
                                        argumento_costo=costo, argumento_eficiencia=eficiencia, 
                                        argumento_facilidad=facilidad, argumento_tiempo=tiempo)
    db.add(nueva_argumentacion)
    db.commit()
    db.refresh(nueva_argumentacion)
    return nueva_argumentacion

def falsear_alternativas(db: Session):
    alternativas = db.query(Alternativa).all()
    for alternativa in alternativas:
        alternativa.elegida = False
    db.commit()
    return alternativas

def elegir_alternativa(db: Session, id_alternativa: int):
    falsear_alternativas(db)
    alternativa = db.query(Alternativa).filter(Alternativa.id_alternativa == id_alternativa).first()
    if alternativa is None:
        raise HTTPException(status_code=404, detail="Alternativa no encontrada")
    alternativa.elegida = True
    db.commit()
    db.refresh(alternativa)
    return alternativa