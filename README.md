# MIDI Generator

A typical MIDI file can be viewed as a sequence of notes and chords with specified offsets that show their place in a melody. From this point of view, a chord is a group of notes that are played simultaneously. For melody generation, the next note or chord must be predicted based on an already-existing part. It's an example of a `seq2seq` problem and the `GRU` model could be used to solve it. For simplicity’s sake, note offsets in the code do not show the specific place of a note or  chord in a piece, they show the time delay that required before the predicted element is played.

This project shows a simple example of `.mid` files generation. A small model based on `GRU` architecture is used in order to learn patterns (orders of notes and chords) from existing melodies (see data directory).

The project is created from the [Neuro Platform Project Template](https://github.com/neuromation/cookiecutter-neuro-project) and designed to run on [Neuro Platform](https://neu.ro), so you can jump into problem-solving right away using the instruction from `Quick Start` section.

# Quick Start

First, to run this project on [Neuro Platform](https://neu.ro) install the `neuro` client and clone the project repository:

```
pip install -U neuromation
neuro login
git clone git@github.com:neuromation/ml-recipe-midi-generator.git
cd ml-recipe-midi-generator
```

This repository already contains pre-trained models, so that you can run Jupyter Notebook with inference code and play with these models. To do so, just copy the following command:

```
make setup && make upload && make jupyter
```

It will ask you to log in on Neuro Platform when the command is run for the first time. A Github account can be used for this purpose. You also can log in with the `neuro login` command. For a deeper understanding of what this command does and of the project’s structure read the explanation below.

# Development Environment

## Directory structure

| Local directory                      | Description       | Storage URI                                                                  | Environment mounting point |
|:------------------------------------ |:----------------- |:---------------------------------------------------------------------------- |:-------------------------- | 
| `data/`                              | Data              | `storage:midi-generator/data/`                              | `/midi-generator/data/` | 
| `midi-generator/`                    | Directory with code    | `storage:midi-generator/midi-generator/` | `/midi-generator/cmidi-generator/` |
| `notebooks/`                         | Jupyter notebooks | `storage:midi-generator/notebooks/`                         | `/midi-generator/notebooks/` |
| `results/`                           | Logs and results  | `storage:midi-generator/results/`                           | `/midi-generator/results/` |

## How to train your own model or run an existing model

Follow the instructions below to set up the environment and start a development session.

### Log into Neuro Platform

Before environment setup, platform login is required:

`neuro login`

It can be done with a `Github` account.

### Setup the development environment 

The first thing you need to do is to specify an environment on the `neuro` platform. To do so, run this command in the project’s root directory:
   
`make setup`

What happens during this command:

* Several files from the local project are uploaded to the platform storage (namely, `requirements.txt`, 
  `apt.txt`, `setup.cfg`).
* A new job is started in our [base environment](https://hub.docker.com/r/neuromation/base). 
* Pip requirements from `requirements.txt` and apt applications from `apt.txt` are installed in this environment.
* The updated environment is saved under a new project-dependent name and is used further on.

After that, the image with the name `neuromation-midi-generator` will be created. To see a list of images 
the followed command may be used:

`neuro image ls`

### Uploading / Downloading Resources

After the development environment is set up, the next step is to upload repository resources on the platform with:

`make upload`

This command will upload all repository directories on the platform. To specify exactly what you want to upload:

| Command                      | Uploaded directory       | 
|:---------------------------- |:-------------------------| 
| `make upload-code`           | `midi-generator`         | 
| `make upload-data`           | `data`                   |
| `make upload-notebooks`      | `notebooks`              | 
| `make upload-results`        | `results`                | 

**WARNING:** After each local code modification, you must update the code on the platform by uploading it. 
Resources also can be downloaded with the make download* command.

### Generate a new MIDI file

To generate a new midi file you can run a job on the platform:

`make generate`

After the command is executed, download the resulting file from the platform: `make download-results`. The result can be opened with `timidity`. To setup generation parameters, modify the `generate_config.cfg` file, but do not forget to upload it onto the platform after modification.

### Model training

You can also train your own model. To do so, use the following command:

`make training CONFIG_NAME=base_train_config.cfg`

To specify model and training parameters, modify the `base_train_config.cfg` file. If you want to change the training config, just specify the `CONFIG_NAME` variable in the command (see `midi-generator/configs` for the full list of available predefined train configs). The training process can be followed with TensorBoard:

`make tensorboard`

### Development mode

Remote terminal can be run to execute code manually:

`make developing && connect-developing`

All modified code can be downloaded on a local machine with the `make download` command.

### Run Jupyter with GPU 

`make jupyter`

* The content of `code` and `notebooks` directories is uploaded to the platform storage.
* A job with Jupyter is started, and its web interface is opened in the local web browser window.

### Kill Jupyter

`make kill-jupyter`

* The job with Jupyter Notebooks is terminated. The notebooks are saved on the platform storage. You may run 
  `make download-notebooks` to download them to the local `notebooks/` directory.

### Customization

To modify listed above commands or clarify what they do, see `Makefile`. 
