from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .orm import Base

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
