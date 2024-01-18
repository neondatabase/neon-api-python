gen-model: fetch-v2-schema
	datamodel-codegen \
	--input v2.json \
	--input-file-type jsonschema \
	--collapse-root-models \
	--output-model-type pydantic_v2.BaseModel \
	--output neon_client/schema.py \
	--use-standard-collections \
	--output-model-type pydantic_v2.BaseModel \
	--input-file-type openapi \
	# --use-standard-collections \
	--use-union-operator \
	--target-python-version 3.11 \
	--use-schema-description \
	--snake-case-field \
	--enable-version-header \
  	--use-double-quotes \
  	--allow-population-by-field-name \
  	--use-title-as-name \
	--reuse-model \
	--field-constraints \
	--disable-appending-item-suffix \
	--allow-extra-fields \
	--capitalise-enum-members \
	--use-unique-items-as-set \
	--set-default-enum-member \
	--enum-field-as-literal one \
	--openapi-scopes {schemas,paths,tags,parameters} \
	--use-operation-id-as-name \

	# --field-constraints \
	# --use-annotated \



fetch-v2-schema:
	curl -O https://neon.tech/api_spec/release/v2.json
