from gobupload.alembic_utils import (
    get_query_split_json_column,
    get_query_merge_columns_to_jsonb_column,
    RenamedRelation,
    upgrade_relations,
    downgrade_relations
)

renamed_relations = [
    % for relation_rename in relation_renames:
    RenamedRelation(
        table_name="${relation_rename["table_name"]}",
        old_column="${relation_rename["old_column"]}",
        new_column="${relation_rename["new_column"]}",
        old_relation_table="${relation_rename["old_relation_table"]}",
        new_relation_table="${relation_rename["new_relation_table"]}"
    ),
    % endfor
]

def upgrade():
    % for add_column in add_columns:
    op.add_column('${add_column["table_name"]}', sa.Column('${add_column["column_name"]}', sa.${add_column["sqlalchemy_type"]}(), autoincrement=False, nullable=True))
    % endfor

    % for split in split_json:
    # Split json column ${split["column_name"]} into separate columns
    % for prop_name, prop in split["properties"].items():
    op.add_column('${split["table_name"]}', sa.Column('${prop_name}', sa.${prop}(), autoincrement=False, nullable=True))
    % endfor
    op.execute(get_query_split_json_column('${split["table_name"]}', '${split["column_name"]}', {
    % for from_json_prop, to_column in split["mapping"].items():
        '${from_json_prop}': '${to_column}',
    % endfor
    }, {
    % for json_field, type in split["types"].items():
        '${json_field}': '${type}',
    % endfor
    }))
    op.execute("ALTER TABLE ${split["table_name"]} DROP COLUMN ${split["column_name"]} CASCADE")

    % endfor
    upgrade_relations(op, renamed_relations)

def downgrade():
    downgrade_relations(op, renamed_relations)

    % for split in split_json:
    # Unsplit json column ${split["column_name"]} from separate columns
    op.add_column('${split["table_name"]}', sa.Column('${split["column_name"]}', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.execute(get_query_merge_columns_to_jsonb_column('${split["table_name"]}', '${split["column_name"]}', {
    % for from_json_prop, to_column in split["mapping"].items():
        '${from_json_prop}': '${to_column}',
    % endfor
    }))
    % for prop_name, prop in split["properties"].items():
    op.drop_column('${split["table_name"]}', '${prop_name}')
    % endfor

    % endfor

    % for add_column in add_columns:
    op.drop_column('${add_column["table_name"]}', '${add_column["column_name"]}')
    % endfor
