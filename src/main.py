from fastapi import FastAPI

from mapper import MetadataMapper
from schema.input import Input
from version import get_version

app = FastAPI()


@app.get("/version")
async def info():
    result = get_version()
    return {"version": result}


# TODO: use Response model
@app.post("/mapper")
def map_metadata(input_data: Input):
    mapper = MetadataMapper(input_data.metadata, input_data.template,
                            input_data.mapping)
    mapper.map_metadata()
    mapper.remove_empty_fields()
    return mapper.template
