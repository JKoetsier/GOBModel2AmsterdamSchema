from gobcore.model import GOBModel
from gobcore.model.relations import _get_destination, _get_relation_name


def get_new_relation_name(gob_model: GOBModel, catalog_name: str, collection_name: str, old_column_name: str, new_column_name: str):
    """Logic copied and adjusted based on get_relation_name in GOB-Core"""
    catalog = gob_model.get_catalog(catalog_name)
    collection = gob_model.get_collection(catalog_name, collection_name)
    reference = [reference for name, reference in collection['attributes'].items() if name == old_column_name][0]
    dst_catalog_name, dst_collection_name = reference['ref'].split(':')

    src = {
        "catalog": catalog,
        "catalog_name": catalog_name,
        "collection": collection,
        "collection_name": collection_name
    }
    dst = _get_destination(gob_model, dst_catalog_name, dst_collection_name)
    return _get_relation_name(src=src,
                              dst=dst,
                              reference_name=new_column_name)
