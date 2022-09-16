from typing import Literal, Union

import yaml
from pydantic import BaseModel
from gobcore.model.amschema.model import Properties


class RenameAction(BaseModel):
    type: Literal["rename"]
    old_column_name: str
    new_column_name: str


class AddAction(BaseModel):
    type: Literal["add"]
    property: Properties
    column_name: str


class SplitJsonAction(BaseModel):
    type: Literal["split_json"]
    column_name: str
    mapping: dict[str, str]
    types: dict[str, str]
    properties: dict[str, Properties]


class Entity(BaseModel):
    catalog: str
    collection: str
    schema_version: str
    actions: list[Union[RenameAction, AddAction, SplitJsonAction]]


class MigrationDefinition(BaseModel):
    entities: list[Entity]


def load_definition(filelocation: str) -> MigrationDefinition:
    with open(filelocation) as f:
        mdef = yaml.safe_load(f)
        return MigrationDefinition.parse_obj(mdef)
