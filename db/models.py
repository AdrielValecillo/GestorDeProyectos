from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from db.db import Base
from sqlalchemy.orm import relationship

class Propuesta(Base):
    __tablename__ = 'propuestas'

    id_proyecto = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String)
    alternativas_ia = Column(String)

    alternativas = relationship("Alternativa", back_populates="propuesta")


class Alternativa(Base):
    __tablename__ = 'alternativas'

    id_alternativa = Column(Integer, primary_key=True, index=True)
    id_proyecto = Column(Integer, ForeignKey('propuestas.id_proyecto'))
    nombre_alternativa = Column(String)
    costo = Column(Integer)
    eficiencia = Column(Integer)
    facilidad_implementacion = Column(Integer)
    tiempo = Column(Integer)
    elegida = Column(Boolean, default=False)


    propuesta = relationship("Propuesta", back_populates="alternativas")
    argumentaciones = relationship("Argumentacion", back_populates="alternativa")


class Argumentacion(Base):
    __tablename__ = 'argumentaciones'

    id_argumentacion = Column(Integer, primary_key=True, index=True)
    id_alternativa = Column(Integer, ForeignKey('alternativas.id_alternativa'))
    argumento = Column(String)
    argumento_costo = Column(String)
    argumento_eficiencia = Column(String)
    argumento_facilidad = Column(String)
    argumento_tiempo = Column(String)

    alternativa = relationship("Alternativa", back_populates="argumentaciones")
