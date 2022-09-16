
from gobcore.model import GOBModel, Schema
from gobcore.model.amschema.model import Dataset
from gobcore.model.schema import load_schema
from gobcore.model.amschema.repo import AMSchemaRepository

from migrate_util.definition import Entity, MigrationDefinition


def get_gob_migrated_attributes(entity: Entity, gob_model: GOBModel, dataset: Dataset):
    collection = gob_model.get_collection(entity.catalog, entity.collection)
    attrs = {**collection['attributes']}

    for action in entity.actions:
        if action.type == "rename":
            attrs[action.new_column_name] = attrs[action.old_column_name]
            del attrs[action.old_column_name]
        elif action.type == "add":
            attrs[action.column_name] = action.property.gob_representation(dataset)
        elif action.type == "split_json":
            for attr_name, property in action.properties.items():
                attrs[attr_name] = property.gob_representation(dataset)
            del attrs[action.column_name]
    return attrs


def validate_entity(entity: Entity, gob_model: GOBModel):
    schema = Schema(
        datasetId=f"{entity.catalog}_azure",
        tableId=entity.collection,
        version=entity.schema_version
    )

    to_gob = load_schema(schema)

    repo = AMSchemaRepository()
    table, dataset = repo.get_schema(schema)

    migrated_attrs = get_gob_migrated_attributes(entity, gob_model, dataset)
    amsschema_attrs = to_gob['attributes']
    migrated_types = {k: v["type"] for k, v in migrated_attrs.items()}
    amschema_types = {k: v["type"] for k, v in amsschema_attrs.items()}

    if migrated_types != amschema_types:
        print(f"The actions defined for {entity.catalog} {entity.collection} in the definition file do not result in the correct AMS Schema")
        print("GOB Attributes after applying the transformations in the definition file:")
        print(migrated_types)
        print("Amsterdam schema attributes that we want:")
        print(amschema_types)
        print("Differences")

        if sorted(migrated_types.keys()) != sorted(amschema_types.keys()):
            print("Mismatching attributes:")
            print("GOB:", sorted(migrated_types.keys()))
            print("AMS:", sorted(amschema_types.keys()))
        else:
            for key, type_ in amschema_types.items():
                if type_ != migrated_types[key]:
                    print(f"Type for {key} differs. GOB: {migrated_types[key]}, AMS: {type_}")
        exit(1)


def validate_migration_definition(definition: MigrationDefinition, gob_model: GOBModel):
    for entity in definition.entities:
        print(f"Validating {entity.catalog} {entity.collection}..")
        validate_entity(entity, gob_model)
    print("Validation successful")
