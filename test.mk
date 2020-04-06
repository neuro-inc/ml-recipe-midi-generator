NOTEBOOKS_DIR=notebooks
PROJECT_PATH_ENV?=/midi-generator

.PHONY: test_jupyter_demo
test_jupyter_demo:
	make jupyter \
       JUPYTER_CMD='bash -c " \
         export DEBIAN_FRONTEND=noninteractive && \
         apt-get -qq update && \
         apt-get -qq install -y --no-install-recommends pandoc && \
         jupyter nbconvert \
            --execute \
            --no-prompt \
            --no-input \
            --to=asciidoc \
            --output=/tmp/out \
            $(PROJECT_PATH_ENV)/$(NOTEBOOKS_DIR)/inference.ipynb \
            2>&1 | grep -P \"Writing \d+ bytes to /tmp/out.asciidoc\" && \
          echo OK \
       "'
