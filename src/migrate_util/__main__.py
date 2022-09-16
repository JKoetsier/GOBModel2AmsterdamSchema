import sys

from gobcore.model import GOBModel

from migrate_util.migrate import migrate
from migrate_util.definition import load_definition
from migrate_util.validate import validate_migration_definition

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide definition file as argument")
        exit(1)

    definition = load_definition(sys.argv[1])
    gob_model = GOBModel(legacy=True)

    validate_migration_definition(definition, gob_model)
    migrate(definition, gob_model)
