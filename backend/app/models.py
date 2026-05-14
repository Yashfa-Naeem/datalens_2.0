from sqlalchemy import Column, Integer, String, Text
from app.database import Base
class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    table_name = Column(String, unique=True)
    columns = Column(Text)
    row_count = Column(Integer)