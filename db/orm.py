from typing import List
from sqlalchemy import (
    MetaData,
    UniqueConstraint,
    Column,
    Integer,
    Boolean,
    String,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, declarative_base, relationship

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    report_sections: Mapped[List["ReportSection"]] = relationship(
        "ReportSection", back_populates="report"
    )
    sections: Mapped[List["Section"]] = relationship(
        "Section", secondary="report_section", viewonly=True
    )


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    origin_report: Mapped[Report] = relationship(
        "Report",
        secondary="report_section",
        primaryjoin="and_(Section.id==ReportSection.section_id, ReportSection.origin==True)",
        single_parent=True,
        viewonly=True,
    )


class ReportSection(Base):
    __tablename__ = "report_section"
    __table_args__ = (UniqueConstraint("section_id", "origin"),)
    origin = Column(Boolean, default=False)
    report_id = Column(Integer, ForeignKey("reports.id"), primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id"), primary_key=True)
    position = Column(Integer)
    report = relationship("Report", back_populates="report_sections")
    section = relationship("Section")
