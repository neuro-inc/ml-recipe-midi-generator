NOTEBOOKS_DIR=notebooks
PROJECT_PATH_ENV=/midi-generator

.PHONY: test_jupyter_demo
test_jupyter_demo:
	make jupyter \
         JUPYTER_CMD="bash -c ' \
             pip3 install --progress-bar=off pandoc && \
             jupyter nbconvert \
             --execute \
             --no-prompt \
             --no-input \
             --to=asciidoc \
             --output=out \
             $(PROJECT_PATH_ENV)/$(NOTEBOOKS_DIR)/inference.ipynb \
        '"
