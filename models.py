from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class AnalysisHistory(Base):
    __tablename__ = 'analysis_history'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    filename = Column(Text)
    transaction_count = Column(Integer)
    item_count = Column(Integer)
    min_support = Column(Float)
    min_confidence = Column(Float)
    min_lift = Column(Float)
    frequent_itemset_count = Column(Integer)
    rule_count = Column(Integer)
    
    rules = relationship("SavedRule", back_populates="analysis", cascade="all, delete-orphan")
    itemsets = relationship("SavedItemset", back_populates="analysis", cascade="all, delete-orphan")
    time_series = relationship("TimeSeriesAnalysis", back_populates="analysis", cascade="all, delete-orphan")

class SavedRule(Base):
    __tablename__ = 'saved_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey('analysis_history.id', ondelete="CASCADE"))
    antecedents = Column(Text)
    consequents = Column(Text)
    support = Column(Float)
    confidence = Column(Float)
    lift = Column(Float)
    
    analysis = relationship("AnalysisHistory", back_populates="rules")

class SavedItemset(Base):
    __tablename__ = 'saved_itemsets'
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey('analysis_history.id', ondelete="CASCADE"))
    itemset = Column(Text)
    support = Column(Float)
    
    analysis = relationship("AnalysisHistory", back_populates="itemsets")

class TimeSeriesAnalysis(Base):
    __tablename__ = 'time_series_analysis'
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey('analysis_history.id', ondelete="CASCADE"))
    timestamp_col = Column(Text)
    time_unit = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    time_periods = Column(Integer)
    period_data = Column(Text)  # JSON string of period details
    
    analysis = relationship("AnalysisHistory", back_populates="time_series")
