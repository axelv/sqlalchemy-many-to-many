from sqlalchemy import Boolean, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import Mapped, declarative_base, relationship, mapped_column


metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Template(Base):
    __tablename__ = "template"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # cross version uuid
    identifier: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="uuid_generate_v4()"
    )
    title: Mapped[str] = mapped_column(String(256), nullable=True)
    children: Mapped["TemplateComponent"] = relationship(
        "TemplateComponent",
        secondary="template_component_association",
        primaryjoin="and_(TemplateComponentAssociation.parent_component_id==None, TemplateComponentAssociation.template_id==Template.id)",
        secondaryjoin="TemplateComponentAssociation.child_component_id==TemplateComponent.id",
        order_by="TemplateComponentAssociation.position",
        viewonly=True,
        uselist=True,
    )
    child_associations: Mapped[list["TemplateComponentAssociation"]] = relationship(
        "TemplateComponentAssociation",
        primaryjoin="and_(TemplateComponentAssociation.parent_component_id==None, TemplateComponentAssociation.template_id==Template.id)",
        foreign_keys="TemplateComponentAssociation.template_id",
        uselist=True,
    )


class TemplateComponentAssociation(Base):
    __tablename__ = "template_component_association"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("template.id"), nullable=True
    )
    child_component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("template_component.id")
    )
    parent_component_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("template_component.id"), nullable=True
    )
    origin: Mapped[bool] = mapped_column(Boolean, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    template: Mapped[Template] = relationship(Template, foreign_keys=[template_id])
    child: Mapped["TemplateComponent"] = relationship(
        "TemplateComponent",
        foreign_keys=[child_component_id],
    )
    parent: Mapped["TemplateComponent"] = relationship(
        "TemplateComponent", foreign_keys=[parent_component_id]
    )


class TemplateComponent(Base):
    __tablename__ = "template_component"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=True)
    template_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("template.id"), nullable=True
    )
    # cross version uuid
    identifier: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="uuid_generate_v4()"
    )
    template: Mapped[Template] = relationship(Template, foreign_keys=[template_id])
    origin_parent: Mapped["TemplateComponent"] = relationship(
        "TemplateComponent",
        secondary="template_component_association",
        primaryjoin="and_(TemplateComponentAssociation.origin==True, TemplateComponentAssociation.child_component_id==TemplateComponent.id)",
        foreign_keys="TemplateComponentAssociation.child_component_id",
        uselist=False,
        single_parent=True,
        viewonly=True,
    )

    children: Mapped["TemplateComponent"] = relationship(
        "TemplateComponent",
        secondary="template_component_association",
        order_by=TemplateComponentAssociation.position,
        viewonly=True,
        uselist=True,
        primaryjoin="TemplateComponentAssociation.parent_component_id==TemplateComponent.id",
        secondaryjoin="TemplateComponentAssociation.child_component_id==TemplateComponent.id",
    )
    child_associations: Mapped["TemplateComponentAssociation"] = relationship(
        "TemplateComponentAssociation",
        foreign_keys=TemplateComponentAssociation.parent_component_id,
        uselist=True,
    )
