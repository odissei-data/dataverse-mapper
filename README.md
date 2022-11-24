# dataverse-mapper
## Description
The dataverse-mapper API can be used to map any JSON metadata to JSON metadata formatted for Dataverse.
The metadata file will be formatted according to what's expected by the [Dataverse Native API](https://guides.dataverse.org/en/latest/api/native-api.html#import-a-dataset-into-a-dataverse-collection).
If you have XML metadata you can use the [DANS transformer service](https://transformer.labs.dans.knaw.nl/docs#/Transform/Transform_xml_to_json_format__transform_xml_to_json_post) to map it to JSON.

## Frameworks
This project uses:
- Python 3.9
- FastAPI
- Poetry

## Setup
The default port in the example .env is 8080, change it to fit your needs.
1. `cp dot_env_example .env`
2. `make build`


## End-points
### Version
Returns the current version of the API

### Mapper
Maps JSON metadata to JSON metadata formatted for Dataverse.
#### Parameters
- metadata - [EASY metadata example](https://github.com/odissei-data/dataverse-mapper/blob/development/test-data/input-data/easy-test-metadata.json) - The input metadata describing a dataset in JSON.
- template - [EASY template example](https://github.com/odissei-data/dataverse-mapper/blob/development/test-data/template-data/cbs_dataverse_template.json) - A template with the value you expect to map from the input metadata.
- mapping - [EASY mapping example](https://github.com/odissei-data/dataverse-mapper/blob/development/test-data/mappings/easy-mapping.json) - A dictionary with key value pairs. The key is the _typeName_ of the field in the template. The value is the path to the value in the input metadata.
- has_existing_doi - e.g. _true_ - A boolean specifying if the metadata will contain a persistent identifier mapped to the _datasetPersistentId_ field in the template.

#### Return value
When successful, the API call will return a JSON body formatted for ingestion into Dataverse.
The call will return an exception on a failed attempt further elaborating what went wrong.
