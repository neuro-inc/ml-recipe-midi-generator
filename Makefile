BASE_ENV_VERSION=v1.5

##### PATHS #####

DATA_DIR?=data
CODE_DIR?=midi-generator
NOTEBOOKS_DIR?=notebooks
RESULTS_DIR?=results

PROJECT_FILES=requirements.txt apt.txt setup.cfg

PROJECT_PATH_STORAGE?=storage:midi-generator

PROJECT_PATH_ENV?=/midi-generator

##### JOB NAMES #####

PROJECT_POSTFIX?=midi-generator

SETUP_JOB?=setup-$(PROJECT_POSTFIX)
TRAINING_JOB?=training-$(PROJECT_POSTFIX)
GENERATE_JOB?=generate-$(PROJECT_POSTFIX)
DEVELOPING_JOB?=developing-$(PROJECT_POSTFIX)
JUPYTER_JOB?=jupyter-$(PROJECT_POSTFIX)
TENSORBOARD_JOB?=tensorboard-$(PROJECT_POSTFIX)
FILEBROWSER_JOB?=filebrowser-$(PROJECT_POSTFIX)

##### ENVIRONMENTS #####

BASE_ENV_NAME?=neuromation/base:$(BASE_ENV_VERSION)
CUSTOM_ENV_NAME?=image:neuromation-$(PROJECT_POSTFIX)

##### VARIABLES YOU MAY WANT TO MODIFY #####

# Location of your dataset on the platform storage. Example:
# DATA_DIR_STORAGE?=storage:datasets/cifar10
DATA_DIR_STORAGE?=$(PROJECT_PATH_STORAGE)/$(DATA_DIR)

# The type of the training machine (run `neuro config show` to see the list of available types).
TRAINING_MACHINE_TYPE?=gpu-small
# HTTP authentication (via cookies) for the job's HTTP link.
# Set `HTTP_AUTH?=--no-http-auth` to disable any authentication.
# WARNING: removing authentication might disclose your sensitive data stored in the job.
HTTP_AUTH?=--http-auth
# Command to run training inside the environment. Example:
CONFIG_NAME=base_train_config.cfg
TRAINING_COMMAND="bash -c 'cd $(PROJECT_PATH_ENV) && python -u $(CODE_DIR)/train.py -c $(CODE_DIR)/configs/$(CONFIG_NAME)'"
GENERATE_COMMAND="bash -c 'cd $(PROJECT_PATH_ENV) && python -u $(CODE_DIR)/generate.py -c $(CODE_DIR)/configs/generate_config.cfg'"

JUPYTER_CMD=jupyter notebook --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token= --notebook-dir=$(PROJECT_PATH_ENV)

##### COMMANDS #####

APT?=apt-get -qq
PIP?=pip install --progress-bar=off
NEURO?=neuro

##### HELP #####
.PHONY: fffalso
fffalso:
	@echo doing fffalso
	false

.PHONY: help
help:
	@# generate help message by parsing current Makefile
	@# idea: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -hE '^[a-zA-Z_-]+:\s*?### .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

##### SETUP #####

.PHONY: setup
setup: ### Setup remote environment
	$(NEURO) kill $(SETUP_JOB) >/dev/null 2>&1 || :
	$(NEURO) run \
		--name $(SETUP_JOB) \
		--preset cpu-small \
		--detach \
		--volume $(PROJECT_PATH_STORAGE):$(PROJECT_PATH_ENV):ro \
		$(BASE_ENV_NAME) \
		'sleep 1h'
	$(NEURO) mkdir $(PROJECT_PATH_STORAGE) | true
	$(NEURO) mkdir $(PROJECT_PATH_STORAGE)/$(CODE_DIR) | true
	$(NEURO) mkdir $(PROJECT_PATH_STORAGE)/$(DATA_DIR) | true
	$(NEURO) mkdir $(PROJECT_PATH_STORAGE)/$(NOTEBOOKS_DIR) | true
	for file in $(PROJECT_FILES); do $(NEURO) cp ./$$file $(PROJECT_PATH_STORAGE)/$$file; done
	$(NEURO) exec --no-tty --no-key-check $(SETUP_JOB) "bash -c 'export DEBIAN_FRONTEND=noninteractive && $(APT) update && cat $(PROJECT_PATH_ENV)/apt.txt | xargs -I % $(APT) install --no-install-recommends % && $(APT) clean && $(APT) autoremove && rm -rf /var/lib/apt/lists/*'"
	$(NEURO) exec --no-tty --no-key-check $(SETUP_JOB) "bash -c '$(PIP) -r $(PROJECT_PATH_ENV)/requirements.txt'"
ifdef __BAKE_SETUP
	make __bake
endif
	$(NEURO) --network-timeout 300 job save $(SETUP_JOB) $(CUSTOM_ENV_NAME)
	$(NEURO) kill $(SETUP_JOB)

.PHONY: __bake
__bake: upload-code upload-data upload-notebooks upload-results
	echo "#!/usr/bin/env bash" > /tmp/jupyter.sh
	echo "jupyter notebook \
            --no-browser \
            --ip=0.0.0.0 \
            --allow-root \
            --NotebookApp.token= \
            --NotebookApp.default_url=/notebooks/project-local/notebooks/inference.ipynb \
            --NotebookApp.shutdown_no_activity_timeout=7200 \
            --MappingKernelManager.cull_idle_timeout=7200 \
" >> /tmp/jupyter.sh
	$(NEURO) cp /tmp/jupyter.sh $(PROJECT_PATH_STORAGE)/jupyter.sh
	$(NEURO) exec --no-tty --no-key-check $(SETUP_JOB) \
	    "bash -c 'mkdir /project-local; cp -R -T $(PROJECT_PATH_ENV) /project-local'"
	$(NEURO) exec --no-tty --no-key-check $(SETUP_JOB) \
           "jupyter trust /project-local/notebooks/inference.ipynb"


##### STORAGE #####

.PHONY: upload-code
upload-code:  ### Upload code directory to the platform storage
	$(NEURO) cp --recursive --update --no-target-directory $(CODE_DIR) $(PROJECT_PATH_STORAGE)/$(CODE_DIR)

.PHONY: clean-code
clean-code:  ### Delete code directory from the platform storage
	$(NEURO) rm --recursive $(PROJECT_PATH_STORAGE)/$(CODE_DIR)/*

.PHONY: upload-data
upload-data:  ### Upload data directory to the platform storage
	$(NEURO) cp --recursive --update --no-target-directory $(DATA_DIR) $(DATA_DIR_STORAGE)

.PHONY: clean-data
clean-data:  ### Delete data directory from the platform storage
	$(NEURO) rm --recursive $(DATA_DIR_STORAGE)/*

.PHONY: upload-notebooks
upload-notebooks:  ### Upload notebooks directory to the platform storage
	$(NEURO) cp --recursive --update --no-target-directory $(NOTEBOOKS_DIR) $(PROJECT_PATH_STORAGE)/$(NOTEBOOKS_DIR)

.PHONY: download-notebooks
download-notebooks:  ### Download notebooks directory from the platform storage
	$(NEURO) cp --recursive --update --no-target-directory $(PROJECT_PATH_STORAGE)/$(NOTEBOOKS_DIR) $(NOTEBOOKS_DIR)

.PHONY: clean-notebooks
clean-notebooks:  ### Delete notebooks directory from the platform storage
	$(NEURO) rm --recursive $(PROJECT_PATH_STORAGE)/$(NOTEBOOKS_DIR)/*

.PHONY: upload-results
upload-results:  ### Upload results directory to the platform storage
	$(NEURO) cp --recursive --update --no-target-directory $(RESULTS_DIR) $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR)

.PHONY: download-results
download-results:  ### Download results directory from the platform storage
	$(NEURO) cp --recursive --update --no-target-directory $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR) $(RESULTS_DIR)

.PHONY: upload  ### Upload code, data, and notebooks directories to the platform storage
upload: upload-code upload-data upload-notebooks upload-results

.PHONY: clean  ### Delete code, data, and notebooks directories from the platform storage
clean: clean-code clean-data clean-notebooks

##### JOBS #####

.PHONY: training
training:  ### Run a training job
	$(NEURO) run \
		--name $(TRAINING_JOB) \
		--preset $(TRAINING_MACHINE_TYPE) \
		--volume $(DATA_DIR_STORAGE):$(PROJECT_PATH_ENV)/$(DATA_DIR):ro \
		--volume $(PROJECT_PATH_STORAGE)/$(CODE_DIR):$(PROJECT_PATH_ENV)/$(CODE_DIR):ro \
		--volume $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR):$(PROJECT_PATH_ENV)/$(RESULTS_DIR):rw \
		--env EXPOSE_SSH=yes \
		$(CUSTOM_ENV_NAME) \
		$(TRAINING_COMMAND)

.PHONY: kill-training
kill-training:  ### Terminate the training job
	$(NEURO) kill $(TRAINING_JOB) || :

.PHONY: connect-training
connect-training:  ### Connect to the remote shell running on the training job
	$(NEURO) exec --no-tty --no-key-check $(TRAINING_JOB) bash

.PHONY: generate
generate:  ### Run a generate job
	$(NEURO) run \
		--name $(GENERATE_JOB) \
		--preset $(TRAINING_MACHINE_TYPE) \
		--volume $(DATA_DIR_STORAGE):$(PROJECT_PATH_ENV)/$(DATA_DIR):ro \
		--volume $(PROJECT_PATH_STORAGE)/$(CODE_DIR):$(PROJECT_PATH_ENV)/$(CODE_DIR):ro \
		--volume $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR):$(PROJECT_PATH_ENV)/$(RESULTS_DIR):rw \
		--env EXPOSE_SSH=yes \
		$(CUSTOM_ENV_NAME) \
		$(GENERATE_COMMAND)

.PHONY: kill-generate
kill-generate: ### Kill the generate job
	$(NEURO) kill $(GENERATE_JOB) || :

.PHONY: connect-generate
connect-generate: ### Connect to the developing job (open terminal on remote server)
	$(NEURO) exec --no-tty --no-key-check $(GENERATE_JOB) bash

.PHONY: developing
developing: ### Run environment with bash terminal
	$(NEURO) run \
		--name $(DEVELOPING_JOB) \
		--preset $(TRAINING_MACHINE_TYPE) \
		--volume $(DATA_DIR_STORAGE):$(PROJECT_PATH_ENV)/$(DATA_DIR):ro \
		--volume $(PROJECT_PATH_STORAGE)/$(CODE_DIR):$(PROJECT_PATH_ENV)/$(CODE_DIR):rw \
		--volume $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR):$(PROJECT_PATH_ENV)/$(RESULTS_DIR):rw \
		--env EXPOSE_SSH=yes \
		--http 8888 \
		--no-http-auth \
		--detach \
		$(CUSTOM_ENV_NAME) \
		'bash'

.PHONY: kill-developing
kill-developing: ### Kill a developing job
	neuro kill $(DEVELOPING_JOB) || :

.PHONY: connect-developing
connect-developing: ### Connect a developing job
	neuro exec -t $(DEVELOPING_JOB) bash

.PHONY: jupyter
jupyter: upload-code upload-notebooks ### Run a job with Jupyter Notebook and open UI in the default browser
	$(NEURO) run \
		--name $(JUPYTER_JOB) \
		--preset $(TRAINING_MACHINE_TYPE) \
		--http 8888 \
		$(HTTP_AUTH) \
		--browse \
		--volume $(DATA_DIR_STORAGE):$(PROJECT_PATH_ENV)/$(DATA_DIR):ro \
		--volume $(PROJECT_PATH_STORAGE)/$(CODE_DIR):$(PROJECT_PATH_ENV)/$(CODE_DIR):rw \
		--volume $(PROJECT_PATH_STORAGE)/$(NOTEBOOKS_DIR):$(PROJECT_PATH_ENV)/$(NOTEBOOKS_DIR):rw \
		--volume $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR):$(PROJECT_PATH_ENV)/$(RESULTS_DIR):rw \
		$(CUSTOM_ENV_NAME) \
		$(JUPYTER_CMD)

.PHONY: kill-jupyter
kill-jupyter:  ### Terminate the job with Jupyter Notebook
	$(NEURO) kill $(JUPYTER_JOB) || :

.PHONY: connect-jupyter
connect-jupyter:  ### Connect to the remote shell running on the jupyter job
	$(NEURO) exec $(JUPYTER_JOB) bash

.PHONY: tensorboard
tensorboard:  ### Run a job with TensorBoard and open UI in the default browser
	$(NEURO) run \
		--name $(TENSORBOARD_JOB) \
		--preset cpu-small \
		--http 6006 \
		$(HTTP_AUTH) \
		--browse \
		--volume $(PROJECT_PATH_STORAGE)/$(RESULTS_DIR):$(PROJECT_PATH_ENV)/$(RESULTS_DIR):ro \
		$(CUSTOM_ENV_NAME) \
		'tensorboard --host=0.0.0.0 --logdir=$(PROJECT_PATH_ENV)/$(RESULTS_DIR)/board'

.PHONY: kill-tensorboard
kill-tensorboard:  ### Terminate the job with TensorBoard
	$(NEURO) kill $(TENSORBOARD_JOB) || :

.PHONY: filebrowser
filebrowser:  ### Run a job with File Browser and open UI in the default browser
	$(NEURO) run \
		--name $(FILEBROWSER_JOB) \
		--preset cpu-small \
		--http 80 \
		$(HTTP_AUTH) \
		--browse \
		--volume $(PROJECT_PATH_STORAGE):/srv:rw \
		filebrowser/filebrowser \
		--noauth

.PHONY: kill-filebrowser
kill-filebrowser:  ### Terminate the job with File Browser
	$(NEURO) kill $(FILEBROWSER_JOB) || :

.PHONY: kill  ### Terminate all jobs of this project
kill: kill-training kill-jupyter kill-generate kill-developing kill-tensorboard kill-filebrowser

##### LOCAL #####

.PHONY: setup-local
setup-local:  ### Install pip requirements locally
	$(PIP) -r requirements.txt

.PHONY: lint
lint:  ### Run static code analysis locally
	flake8 .
	mypy .

##### MISC #####

.PHONY: ps
ps:  ### List all running and pending jobs
	$(NEURO) ps
