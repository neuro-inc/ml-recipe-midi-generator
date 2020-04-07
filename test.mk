include Makefile

CMD_PREPARE=\
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get -qq update && \
  apt-get -qq install -y --no-install-recommends pandoc >/dev/null

CMD_NBCONVERT=\
  jupyter nbconvert \
  --execute \
  --no-prompt \
  --no-input \
  --to=asciidoc \
  --output=/tmp/out \
  $(PROJECT_PATH_ENV)/$(NOTEBOOKS_DIR)/inference.ipynb \
  2>&1 | tee | grep -P \"Writing \d+ bytes to /tmp/out.asciidoc\"


.PHONY: test_jupyter
test_jupyter: JUPYTER_CMD=bash -c "$(CMD_PREPARE) && $(CMD_NBCONVERT)"
test_jupyter: jupyter

.PHONY: test_jupyter_baked
test_jupyter_baked: PROJECT_PATH_ENV=/project-local
test_jupyter_baked:
	neuro run \
		--preset $(TRAINING_MACHINE_TYPE) \
		$(CUSTOM_ENV_NAME) \
		bash -c "$(CMD_PREPARE) && $(CMD_NBCONVERT)"