#
# TEST_ID=$(shell date +%Y%m%d=%H%M%S-%N)
# PROJECT=ml-recipe-midi-generator
# IMAGE_URI=image:$(PROJECT):e2e-$(TEST_ID)
# NOTEBOOKS_DIR=notebooks
#
# setup:
# 	make setup \
# 		__BAKE_SETUP=yes \
# 		CUSTOM_ENV_NAME=$(IMAGE_URI) \
# 		PROJECT_PATH_STORAGE=storage:$(PROJECT)/tests/e2e/$(TEST_ID)
.PHONY: test_jupyter_demo
test_jupyter_demo: setup
	make jupyter \
		JUPYTER_CMD="jupyter nbconvert \
			--execute \
			--no-prompt \
			--no-input \
			--to=asciidoc \
			--output=out \
			$(NOTEBOOKS_DIR)/inference.ipynb \
        "
