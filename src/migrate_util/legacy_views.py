from gobcore.model import GOBModel
from gobcore.model.relations import get_relation_name

from migrate_util.write_file import write_yaml
from migrate_util.definition import Entity

LEGACY_VIEWS_DIR = "legacy_views"


def _create_legacy_view_for_entity_table(entity: Entity, gob_model: GOBModel) -> (str, dict):
    tablename = gob_model.get_table_name(entity.catalog, entity.collection)
    override_columns = {}

    for action in entity.actions:
        if action.type == "add":
            # Nothing to do. Added columns won't show up in legacy view
            pass
        elif action.type == "rename":
            override_columns[action.old_column_name] = action.new_column_name
        elif action.type == "split_json":
            json_build_attrs = ", ".join([f"'{k}', {v}" for k, v in action.mapping.items()])
            override_columns[action.column_name] = f"json_build_object({json_build_attrs})"

    return tablename, {
        "table_name": tablename,
        "override_columns": override_columns,
    }


def _create_legacy_views_for_relations(entity: Entity, gob_model: GOBModel) -> list[(str, dict)]:
    """Only creates views for renamed relations.

    :param entity:
    :param gob_model:
    :return:
    """
    result = []
    for action in [act for act in entity.actions if act.type == "rename"]:

        old_relation_name = get_relation_name(gob_model, entity.catalog, entity.collection, action.old_column_name)

        if old_relation_name:
            new_relation_name = old_relation_name.replace(action.old_column_name, action.new_column_name)

            # Does not always work. Works very basically for now, do check just in case
            assert action.new_column_name in new_relation_name, "This trick didn't work here"

            result.append((
                gob_model.get_table_name("rel", old_relation_name),
                {
                    "table_name": f"rel_{new_relation_name}"
                }
            ))

    return result


def create_legacy_views(entities: list[Entity], gob_model: GOBModel):

    for entity in entities:
        entity_view = _create_legacy_view_for_entity_table(entity, gob_model)
        relation_views = _create_legacy_views_for_relations(entity, gob_model)

        all_views = [entity_view] + relation_views

        for filename, contents in all_views:
            write_yaml(f"{LEGACY_VIEWS_DIR}/{filename}.yaml", contents)
