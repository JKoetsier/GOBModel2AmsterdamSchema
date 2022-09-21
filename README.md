# GobToAmsSchema
Automates the file generation for [Migrating GOB to AMS Schema](https://dev.azure.com/CloudCompetenceCenter/Datateam%20Basis%20en%20Kernregistraties/_wiki/wikis/Datateam-Basis-en-Kernregistraties.wiki/5316/How-to-GOB-Registratie-omzetten-naar-Amsterdam-Schema)

## How it works:
- Define a definitions file. See for example `src/definitions/meetbouten.yaml`. You should define ALL actions necessary
to migrate from GOBModel to Amsterdam Schema. If not, this script will throw an error (because we want everything
covered!)
- Call the script with your definition file. For example, with the `meetbouten.yaml` file:


    docker compose build
    docker compose run app python -m migrate_util /definitions/meetbouten.yaml

- The script will first validate that the migrated GOBModel is indeed equal to the AMS Schema version we're migrating to.
- When the validation has succeeded, the script will place all the generated files in the `output` directory.
- Just follow the steps from the [Migrating GOB to AMS Schema](https://dev.azure.com/CloudCompetenceCenter/Datateam%20Basis%20en%20Kernregistraties/_wiki/wikis/Datateam-Basis-en-Kernregistraties.wiki/5316/How-to-GOB-Registratie-omzetten-naar-Amsterdam-Schema)
documentation and take the necessary files from the `output` directory. Double-check the results. In the import definitions there
may be some `TODO` items left to map new fields, but you'll figure that out. For the alembic migrations you will have to
let alembic generate an empty migration first and copy/paste the generated code in there.

NOTE: If warnings appear when executing the script that relation names are too long, make sure `NameCompressor` in
GOB-Core has some instructions on how to shorten this new name. If this warning is not resolved this may cause issues
further down the line. After adding the name to the `NameCompressor`, double-check the generated alembic migration file.
The old table name may also be compressed there, depending on what you chose to compress. Correct here manually if
necessary.

## Output
This file generates:

- Alembic migrations. Needs copy/pasting in a newly generated empty alembic version file. Create a new empty alembic revision with `alembic revision -m "Revision title"`
- Import definitions. Replace the existing contents with the generated contents. Add the mapping for new columns manually.
- A new JSON file with event migrations. `gobmigrations.json` in GOB-Core should be replaced with this new file. 
Should work without any manual actions.
- Legacy views. Should be a matter of copy/paste in GOB-API. No manual actions necessary.
