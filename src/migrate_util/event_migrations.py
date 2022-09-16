from gobcore.model import GOBModel
from gobcore.model.migrations import GOBMigrations

from migrate_util.definition import Entity
from migrate_util.write_file import write_json

EVENT_MIGRATIONS_DIR = "event_migrations"


def _add_migration(migrations: dict, from_version: str, catalog: str, collection: str, migration: dict):
    if catalog not in migrations:
        migrations[catalog] = {}
    if collection not in migrations[catalog]:
        migrations[catalog][collection] = {}

    migrations[catalog][collection][from_version] = migration


def generate_event_migrations(entities: list[Entity], gob_model: GOBModel):
    migrations = GOBMigrations(gob_model)._data

    for entity in entities:
        current_version = gob_model.get_collection(entity.catalog, entity.collection)['version']
        target_version = f"ams_{entity.schema_version}"

        conversions = []

        for action in entity.actions:
            if action.type == "add":
                conversions.append({
                    "action": "add",
                    "column": action.column_name
                })
            elif action.type == "rename":
                conversions.append({
                    "action": "rename",
                    "old_column": action.old_column_name,
                    "new_column": action.new_column_name
                })
            elif action.type == "split_json":
                # Three actions: add, split_json and del
                for target_col in action.mapping.values():
                    conversions.append({
                        "action": "add",
                        "column": target_col,
                    })
                conversions.append({
                    "action": "split_json",
                    "column": action.column_name,
                    "mapping": {new_column_name: json_attr for json_attr, new_column_name in action.mapping.items()} # Switch order
                })
                conversions.append({
                    "action": "delete",
                    "column": action.column_name
                })

        _add_migration(
            migrations,
            current_version,
            entity.catalog,
            entity.collection, {
                "target_version": target_version,
                "conversions": conversions,
            }
        )

    output_file = f"{EVENT_MIGRATIONS_DIR}/gobmigrations.json"
    write_json(output_file, migrations)
