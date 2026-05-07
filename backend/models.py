from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    saved_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # csv, xlsx, json
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    row_count = Column(Integer, nullable=True)
    col_count = Column(Integer, nullable=True)
    columns_json = Column(Text, nullable=True)   # JSON string of column names & dtypes
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("AnalysisRecord", back_populates="dataset", cascade="all, delete-orphan")


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # eda, stats, anomaly, visualizations
    result_summary = Column(Text, nullable=True)         # JSON summary
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="analyses")
