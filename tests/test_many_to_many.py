import pytest
from db.session import session
from db.orm import Report, ReportSection, Section

@pytest.fixture()
def seed_db():
    first_report = Report(
        name="First Report",
        report_sections=[
            ReportSection(section=Section(content="First Section"), origin=True, position=0),
            ReportSection(section=Section(content="Second Section"), origin=True, position=1),
            ReportSection(section=Section(content="Third Section"), origin=True, position=2),
        ],
    )

    session.add(first_report)
    session.flush()
    second_report = Report(
        name="Second Report",
        report_sections=[
            ReportSection(section=first_report.sections[0], origin=False, position=0),
            ReportSection(section=Section(content="Second Section"), origin=True, position=1),
            ReportSection(section=Section(content="Third Section"), origin=True, position=2),
        ],
    )
    session.add(second_report)
    session.commit()

    yield first_report, second_report


def test_many_to_many(seed_db):
    first_report, second_report = seed_db

    assert first_report.sections[0].id == second_report.sections[0].id, "First section of both reports should be the same"
    assert first_report.sections[0].content == "First Section", "First section of the first report should be 'First Section'"
    assert second_report.sections[1].content == "Second Section", "Second section of the second report should be 'Second Section'"
    assert second_report.sections[2].content == "Third Section", "Third section of the second report should be 'Third Section'"
    assert len(second_report.sections[0].origin_report) == 1, "Second report's first section should have one origin report"
    assert second_report.sections[0].origin_report[0].id == first_report.id, "Second report's first section should be from the first report"
