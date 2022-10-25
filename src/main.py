from fastapi import FastAPI
from mapper import MetadataMapper
from schema.input import JSONInput
from .version import get_version

app = FastAPI()


@app.get("/version")
async def info():
    result = get_version()
    return {"version": result}


@app.post("/mapper")
def map_metadata(json_input: JSONInput):
    mapper = MetadataMapper(json_input.metadata, json_input.template,
                            json_input.mapping)
    mapped_metadata = mapper.map_metadata()
    return mapped_metadata
