gen-model: fetch-v2-schema
	datamodel-codegen --input v2.json --output model.py --use-standard-collections --output models.py \
	--output-model-type pydantic_v2.BaseModel \
	--input-file-type openapi \
	--use-standard-collections \
	--use-union-operator \
	--target-python-version 3.11 \
	--use-schema-description \
	--snake-case-field \
	--enable-version-header \
	--enum-field-as-literal one \
  	--use-double-quotes \
  	--field-constraints \
  	--allow-population-by-field-name \
  	--strict-nullable \
  	--use-title-as-name

fetch-v2-schema:
	curl -O https://neon.tech/api_spec/release/v2.json
