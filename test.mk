PROJECT_PATH_ENV?=/midi-generator
NOTEBOOKS_DIR?=notebooks
CUSTOM_ENV_NAME?=image:neuromation-midi-generator
TRAINING_MACHINE_TYPE?=cpu-small

CMD_REQUIREMENTS=\
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get -qq update && \
  apt-get -qq install -y --no-install-recommends pandoc

CMD_JUPYTER_NBCONVERT=\
  jupyter nbconvert \
  --execute \
  --no-prompt \
  --no-input \
  --to=asciidoc \
  --output=/tmp/out \
  $(PROJECT_PATH_ENV)/$(NOTEBOOKS_DIR)/inference.ipynb \
  2>&1 | grep -P \"NOT Writing \d+ bytes to /tmp/out.asciidoc\"


.PHONY: test_jupyter
test_jupyter:
	make jupyter JUPYTER_CMD='bash -c "$(CMD_REQUIREMENTS) && $(CMD_JUPYTER_NBCONVERT)"'

.PHONY: test_jupyter_baked
test_jupyter_baked:
	neuro run \
		--preset $(TRAINING_MACHINE_TYPE) \
		$(CUSTOM_ENV_NAME) \
		bash -c "$(CMD_REQUIREMENTS) && $(CMD_JUPYTER_NBCONVERT)"