gen-model: fetch-v2-schema
	datamodel-codegen \
	--input v2.json \
	--collapse-root-models \
	--output neon_client/openapi_models.py \
	--use-standard-collections \
	--output-model-type pydantic_v2.BaseModel \
	--input-file-type openapi \
	--use-standard-collections \
	--use-union-operator \
	--target-python-version 3.11 \
	--use-schema-description \
	--snake-case-field \
	--enable-version-header \
  	--use-double-quotes \
  	--field-constraints \
  	--allow-population-by-field-name \
  	--use-title-as-name \
	--reuse-model \
	--field-constraints \
	--disable-appending-item-suffix \
	--allow-extra-fields \
	--use-annotated \
	--capitalise-enum-members \
	--use-unique-items-as-set

fetch-v2-schema:
	curl -O https://neon.tech/api_spec/release/v2.json
