
# SQLAlchemy Many-to-Many Relationship

In this repo, we are exploring the many-to-many relationship in SQLAlchemy. We will create a simple database schema with two tables and a many-to-many relationship between them.
Typical many-to-many relationships are modeled with an association table. The association table is a table that contains foreign keys to the two tables that are related. The association table is used to store the relationships between the two tables.
The goal of this post is to create ORM modols that help us with writing the JOIN-queries that are needed in order to traverse the association table.


## Database Schema

We have two tables: `Report` and `Section`. A report can have multiple sections. Those section have a position to maintain order. A section has only one origin report. But a section can be included in other reports as well.
Traditional SQL to get all sections for a report would look like this:

```sql
SELECT sections.*
FROM sections
JOIN report_section ON sections.id = report_section.section_id
WHERE report_section.report_id = 1
ORDER BY report_section.position;
```

And to get the master report for a section:

```sql
SELECT reports.*
FROM reports
JOIN report_section ON reports.id = report_section.report_id
WHERE report_section.section_id = 1 AND report_section.master = 1;
```
Using ORMs we should be able to simplify this to something like this:

````python
report = session.query(Report).get(1)
sections = report.sections # ordered list of sections
````

```python
section = session.query(Section).get(1)
report = section.master_report # the master report of the section
```

## ORM Models

We will create the following ORM models:

```python
# orm.py
from typing import List, Tuple
from sqlalchemy import (
    MetaData,
    UniqueConstraint,
    create_engine,
    Column,
    Integer,
    Boolean,
    String,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, Session, declarative_base, relationship, sessionmaker

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

class ReportSection(Base):
    __tablename__ = 'report_section'
    master = Column(Boolean, default=False)
    report_id = Column(Integer, ForeignKey('reports.id'), primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.id'), primary_key=True)
    position = Column(Integer)
    origin = Column(Boolean, default=False)
    report = relationship('Report')
    section = relationship('Section')
```

## Create Database

We can create the database and the tables with the following code:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.orm import Base

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
```
## Add a relationship with the association table

We can add a relationship to the `Report` model that allows us to access the section association objects.

```python
class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    report_sections: Mapped[List["ReportSection"]] = relationship(
        "ReportSection", back_populates="report"
    )

This relationship is usefull for creating new reports:

```python
report = Report(name='Report 1')
report.report_sections = [
    ReportSection(section=Section(content='Section 1'), position=1, origin=True),
    ReportSection(section=Section(content='Section 2'), position=2, origin=True),
]

session.add(report)
session.commit()
```

But ideally we would like to have a relationship that allows us to access the sections in order directly:

```python
class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    report_sections: Mapped[List["ReportSection"]] = relationship(
        "ReportSection", back_populates="report"
    )
    sections: Mapped[List["Section"]] = relationship(
        "Section", secondary='report_section', order_by='ReportSection.position', viewonly=True
    )
```
Our model isn't smart enough to determine the correct order of the sections and the origin flag when writing. So we mark the relationship as `viewonly`.

# Add a origin relationship to the section model

We can add a relationship to the `Section` model that allows us to access the report association objects.

```python
class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    origin_report: Mapped[List["Report"]] = relationship(
        "Report",
        secondary='report_section',
        primaryjoin='and_(Section.id == ReportSection.section_id, ReportSection.origin == True)'
        viewonly=True
    )
```

This relationship is usefull for reading the origin report of a section:

```python
first_report = Report(
        name='Report 1'
        report_sections=[
            ReportSection(section=Section(content='Section 1'), position=1, origin=True),
            ReportSection(section=Section(content='Section 2'), position=2, origin=True),
        ]
)
session.add(first_report)
session.flush()
second_report = Report(
        name='Report 2'
        report_sections=[
            ReportSection(section=first_report.sections[0], position=1, origin=False),
            ReportSection(section=Section(content='Section 3'), position=2, origin=True),
        ]
)
session.add(second_report)
session.commit()

assert first_report.sections[0].origin_report == [first_report]
```

## Source code

ORM-models: [orm.py](db/orm.py)
DB session: [session.py](db/session.py)
Tests: [test_orm.py](tests/test_many_to_many.py)
