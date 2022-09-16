from gobconfig.import_.import_config import get_import_definition


from migrate_util.definition import Entity
from migrate_util.write_file import write_json

IMPORT_DEFINITIONS_DIR = "import_definitions"


def fix_import_definitions(entities: list[Entity]):

    for entity in entities:
        importdef = get_import_definition(entity.catalog, entity.collection)
        gob_mapping = importdef["gob_mapping"]

        for action in entity.actions:
            if action.type == "add":
                gob_mapping[action.column_name] = {
                    "source_mapping": "TODO"
                }
            elif action.type == "rename":
                gob_mapping[action.new_column_name] = gob_mapping[action.old_column_name]
                del gob_mapping[action.old_column_name]
            elif action.type == "split_json":
                old_mapping = gob_mapping[action.column_name]

                for json_field, new_column_name in action.mapping.items():
                    gob_mapping[new_column_name] = {
                        "source_mapping": old_mapping["source_mapping"][json_field]
                    }

                del gob_mapping[action.column_name]

        output_file = f"{IMPORT_DEFINITIONS_DIR}/{entity.catalog}_{entity.collection}.json"
        write_json(output_file, importdef)
