import pathlib

from gobcore.model import GOBModel
from gobcore.model.relations import get_relation_name
from gobcore.typesystem import get_gob_type

from mako.template import Template
from migrate_util.definition import Entity
from migrate_util.util import get_new_relation_name
from migrate_util.write_file import write_output_file

ALEMBIC_DIR = "alembic"


def generate_alembic_migrations(entities: list[Entity], gob_model: GOBModel):
    template_path = pathlib.Path(__file__).parent.joinpath('templates/alembic_migrations.py.mako').absolute()
    templ = Template(filename=str(template_path))

    relation_renames = []
    other_renames = []
    add_columns = []
    split_json = []

    for entity in entities:

        for action in entity.actions:
            if action.type == "rename":
                old_relation_name = get_relation_name(gob_model, entity.catalog, entity.collection, action.old_column_name)
                if old_relation_name:
                    new_relation_name = get_new_relation_name(gob_model, entity.catalog, entity.collection, action.old_column_name, action.new_column_name)

                    relation_renames.append({
                        "table_name": gob_model.get_table_name(entity.catalog, entity.collection),
                        "old_column": action.old_column_name,
                        "new_column": action.new_column_name,
                        "old_relation_table": gob_model.get_table_name("rel", old_relation_name),
                        "new_relation_table": gob_model.get_table_name("rel", new_relation_name)
                    })
                else:
                    other_renames.append({
                        "old_column": action.old_column_name,
                        "new_column": action.new_column_name,
                    })
            elif action.type == "add":
                gob_type = get_gob_type(action.property.gob_type)
                add_columns.append({
                    "column_name": action.column_name,
                    "sqlalchemy_type": gob_type.sql_type.__name__,
                    "table_name": gob_model.get_table_name(entity.catalog, entity.collection)
                })
            elif action.type == "split_json":
                split_json.append({
                    "table_name": gob_model.get_table_name(entity.catalog, entity.collection),
                    "column_name": action.column_name,
                    "mapping": action.mapping,
                    "properties": {
                        property_name: get_gob_type(property_.gob_type).sql_type.__name__
                        for property_name, property_ in action.properties.items()
                    },
                    "types": action.types,
                })

    rendered = templ.render(
        relation_renames=relation_renames,
        add_columns=add_columns,
        split_json=split_json
    )

    write_output_file(f"{ALEMBIC_DIR}/alembic_migrations.py", rendered)
