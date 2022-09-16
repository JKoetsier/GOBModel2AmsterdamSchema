import json
import pathlib
import yaml

OUTPUT_DIR = "/output"


def write_output_file(location: str, contents):
    """

    :param location: Relative to the OUTPUT_DIR
    :param contents:
    :return:
    """
    output = pathlib.Path(OUTPUT_DIR).joinpath(location)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        f.write(contents)


def write_yaml(location: str, contents: dict):
    """

    :param location: Relative to the OUTPUT_DIR
    :param contents:
    :return:
    """
    file_contents = yaml.dump(contents, default_flow_style=False, sort_keys=False)
    write_output_file(location, file_contents)


def write_json(location: str, contents: dict):
    """

    :param location: Relative to OUTPUT_DIR
    :param contents:
    :return:
    """
    json_contents = json.dumps(contents, indent=2)
    write_output_file(location, json_contents)
