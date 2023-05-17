# dataverse-mapper

## Description

The dataverse-mapper API can be used to map any JSON metadata to JSON metadata
formatted for Dataverse. The metadata file will be formatted according to
what's expected by the [Dataverse Native API](https://guides.dataverse.org/en/latest/api/native-api.html#import-a-dataset-into-a-dataverse-collection). 
If you have XML metadata you can use the [DANS transformer service](https://transformer.labs.dans.knaw.nl/docs#/Transform/Transform_xml_to_json_format__transform_xml_to_json_post) to map it to JSON.

## Frameworks

This project uses:

- Python 3.9
- FastAPI
- Poetry

## Setup

The default port in the example .env is 8080, change it to fit your needs.

1. `cp dot_env_example .env`
2. `make build

## End-points

### Version

Returns the current version of the API

#### mapper

- metadata - [EASY metadata example](https://github.com/odissei-data/dataverse-mapper/blob/development/test-data/input-data/easy-test-metadata.json) - The input metadata describing a dataset in JSON.
- template - [EASY template example](https://github.com/odissei-data/dataverse-mapper/blob/development/test-data/template-data/cbs_dataverse_template.json) - A template with the value you expect to map from the input metadata.
- mapping - [EASY mapping example](https://github.com/odissei-data/dataverse-mapper/blob/development/test-data/mappings/easy-mapping.json) - A dictionary with key value pairs. The key is the _typeName_ of the field
  in the template. The value is the path to the value in the input
  metadata.
- has_existing_doi - e.g. _true_ - A boolean specifying if the metadata will
  contain a persistent identifier mapped to the _datasetPersistentId_ field in
  the template.

#### Return value

When successful, the API call will return a JSON body formatted for ingestion
into Dataverse. The call will return an exception on a failed attempt further
elaborating what went wrong.

## Mapper

### Mapping file

The mapping file connects the data in the source metadata to the target
template. It contains a dictionary with key/value pairs. Value of those
key/value pairs is a list of paths. These paths are used to find specific data
in the source metadata. The key represents the field in the target template to
which we want to add this data retrieved from the source metadata:
```json
{
  "distributionDate": ["result.Dataontwerpversies.Versie.Dataontwerp.GeldigVanaf"],
  "kindOfData": ["result.Dataontwerpversies.Versie.Dataontwerp.SoortData"],
  "frequencyOfDataCollection": ["result.Dataontwerpversies.Versie.Dataontwerp.TypeVerslagperiode"],
  "samplingProcedure": ["result.Dataontwerpversies.Versie.Dataontwerp.GebruikteMethodologie"],
  "socialScienceNotesSubject": ["result.Dataontwerpversies.Versie.Dataontwerp.Procesverloop"]
}
```

### Compounds
Dataverse JSON contains fields with the _typeClass_ compound. This means that
the value of that field will contain a set of other fields. 
The mapper has multiple ways of handling these compounds.
An example of a compound is the author field in the citation block:

```json
{
  "typeName": "author",
  "multiple": true,
  "typeClass": "compound",
  "value": [
    {
      "authorName": {
        "typeName": "authorName",
        "multiple": false,
        "typeClass": "primitive",
        "value": "LastAuthor1, FirstAuthor1"
      },
      "authorAffiliation": {
        "typeName": "authorAffiliation",
        "multiple": false,
        "typeClass": "primitive",
        "value": "AuthorAffiliation1"
      },
      "authorIdentifierScheme": {
        "typeName": "authorIdentifierScheme",
        "multiple": false,
        "typeClass": "controlledVocabulary",
        "value": "ORCID"
      },
      "authorIdentifier": {
        "typeName": "authorIdentifier",
        "multiple": false,
        "typeClass": "primitive",
        "value": "AuthorIdentifier1"
      }
    }
  ]
}
```

#### Basic compound mapping

 The simple way the mapper maps a compound is to
grab all values for its children from the source metadata. 
 These are put into lists, and the mapper will then
spread these out over multiple objects in the `value` of the compound field. If there are multiple different children for which it retrieved values, it will combine them
based on index.

As an example:
If we find 10 authorName and 5 authorIdentifier values in the source metadata
10 objects are created in the list at `"value": []`. The names and authorID's
will be placed together based on list index so the final 5 object will not
include an authorIdentifier. This way of mapping was made to handle source
metadata where the values meant for the children of the compound are in
completely different parts of the metadata, without a solid way of knowing
what child value should be combined with other child values.

The way to add this mapping to the mapper dictionary is to add the _typeNames_
of the children with their respective paths:

```json
{
  "authorAffiliation": [
    "result.record.metadata.ddi:codeBook.ddi:stdyDscr.ddi:citation.ddi:rspStmt.ddi:AuthEnty.@affiliation"
  ],
  "authorName": [
    "result.record.metadata.ddi:codeBook.ddi:stdyDscr.ddi:citation.ddi:rspStmt.ddi:AuthEnty.#text"
  ]
}
```

#### Object to compound mapping

A different mapping is used for the child fields in a compound that can be
found in the same object in the source metadata. Here the mapping file first
requires the compound _typeName_ and the path to the object in the source
metadata:

```json
{
  "variable": {
    "mapping": "result.Dataontwerpversies.Versie.Dataontwerp.Contextvariabelen.Contextvariabele[*]"
  }
}
```

This allows the mapper to retrieve the objects that can be mapped to the
compound in its entirety. The children fields and their mappings are put inside
this `variable` objects in the `children` key. These paths are then used to 
retrieve the child values from the source object. 
The complete package looks like this:
```json
{
  "variable": {
    "mapping": "result.Dataontwerpversies.Versie.Dataontwerp.Contextvariabelen.Contextvariabele[*]",
    "children": {
      "variableName": ["VerkorteSchrijfwijzeNaamVariabele"],
      "variableLabel": ["LabelVanDeVariabele"],
      "conceptVariableDefinition": ["Variabele.Definitie"],
      "conceptVariableObjecttype": ["VariabeleObjecttypenaam"],
      "conceptVariableValidFrom": ["Variabele.GeldigVanaf"],
      "conceptVariableName": ["Variabele.UniekeNaam"],
      "conceptVariableID": ["Variabele.Id"],
      "conceptVariableVersion": ["Variabele.Versie"],
      "conceptVariableVersionResponsibility": ["Variabele.Eigenaar"],
      "variableProcessingInstruction": ["ToelichtingBijHetGebruik"],
      "variableDataType": ["Datatype"],
      "variableDefinition": ["ToelichtingBijDeDefinitie"],
      "conceptVariableGroeppad": ["Variabele.Variabelengroeppad"],
      "conceptVariableWaardestelselnaam": ["Variabele.Waardestelselnaam"],
      "conceptVariableThema": ["Variabele.Themas.Thema"],
      "variableVolgnummer": ["Volgnummer"],
      "variableTrefwoord": ["Trefwoorden.Trefwoord"]
    }
  }
}
```


