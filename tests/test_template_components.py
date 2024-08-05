
import pytest
from sqlalchemy import select

from template_components.session import session
from template_components.orm import Template, TemplateComponent, TemplateComponentAssociation


@pytest.fixture()
def seed_db():
    templates = [
        Template(
            title="First Template",
            child_associations=[
                TemplateComponentAssociation(
                    origin=True,
                    position=0,
                    child=TemplateComponent(title="First Component"),
                ),
                TemplateComponentAssociation(
                    origin=True,
                    position=1,
                    child=TemplateComponent(title="Second Component"),
                ),
                TemplateComponentAssociation(
                    origin=True,
                    position=2,
                    child=TemplateComponent(title="Third Component"),
                )
            ]
        )
    ]
    session.add_all(templates)
    session.commit()
    yield
    session.rollback()

def test_if_seed_data_is_loaded(seed_db):

    stmt = select(Template)
    result = session.execute(stmt)
    assert result.scalar_one().title == "First Template"
    assert len(result.scalar_one().children) == 3
    assert result.scalar_one().children[0].child.title == "First Component"
