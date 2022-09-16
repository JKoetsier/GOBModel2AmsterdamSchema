from gobcore.model import GOBModel

from migrate_util.alembic_migrations import generate_alembic_migrations
from migrate_util.definition import MigrationDefinition
from migrate_util.event_migrations import generate_event_migrations
from migrate_util.import_definitions import fix_import_definitions
from migrate_util.legacy_views import create_legacy_views


def migrate(definition: MigrationDefinition, gob_model: GOBModel):
    print("Generating alembic migrations..")
    generate_alembic_migrations(definition.entities, gob_model)

    print("Generating fixed import definitions..")
    fix_import_definitions(definition.entities)

    print("Generating event migrations..")
    generate_event_migrations(definition.entities, gob_model)

    print("Generating legacy views..")
    create_legacy_views(definition.entities, gob_model)

    print("Done!")
