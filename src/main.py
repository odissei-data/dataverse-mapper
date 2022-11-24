import json

from fastapi import FastAPI
from pyDataverse.models import Dataset
from pyDataverse.utils import read_file

from mapper import MetadataMapper
from schema.input import Input
from version import get_version

app = FastAPI()


@app.get("/version")
async def info():
    result = get_version()
    return {"version": result}


@app.post("/mapper")
def map_metadata(input_data: Input):
    mapper = MetadataMapper(input_data.metadata, input_data.template,
                            input_data.mapping)
    if input_data.has_existing_doi:
        mapper.template["datasetVersion"][
            "datasetPersistentId"] = mapper.get_persistent_identifier()
    mapped_metadata = mapper.map_metadata()
    return mapped_metadata


def validate_dataverse_json(dataverse_json):
    """ Validates if the json can be imported into dataverse.

    :param dataverse_json:
    :return:
    """

    ds = Dataset()
    filename = "output.json"
    with open(filename, 'w') as outfile:
        json.dump(dataverse_json, outfile)
    ds.from_json(read_file(filename))
    return ds.validate_json()
