test:
	pytest --record-mode=none tests/

fmt:
	ruff format .
ci: 
	pytest --cov=neon_client --record-mode=none tests/

test-build:
	pytest --record-mode=rewrite tests/

gen-model: fetch-v2-schema
	datamodel-codegen \
	--input v2.json \
	--collapse-root-models \
	--output neon_client/schema.py \
	--use-standard-collections \
	--output-model-type dataclasses.dataclass \
	# --input-file-type openapi \
	--use-standard-collections \
	--use-union-operator \
	--target-python-version 3.11 \
	--use-schema-description \
	--snake-case-field \
	--enable-version-header \
  	--use-double-quotes \
  	--allow-population-by-field-name \
  	--use-title-as-name \
	--reuse-model \
	--collapse-root-models \
	# --field-constraints \
	--disable-appending-item-suffix \
	--allow-extra-fields \
	--capitalise-enum-members \
	--allow-extra-fields \
	--use-field-description \
	--use-default \
	--use-enum-values \
	--reuse-model \
	--use-unique-items-as-set \
	--set-default-enum-member \
	--enum-field-as-literal one \
	--allow-extra-fields \
	--openapi-scopes {schemas,paths,tags,parameters} \
	--use-operation-id-as-name \
	--strict-nullable \
	--keep-model-order \
	--field-constraints \

	# --use-annotated \



fetch-v2-schema:
	curl -O https://neon.tech/api_spec/release/v2.json
