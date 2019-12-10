# MIDI Generator

A typical MIDI file can be viewed as a sequence of notes and chords with specified offsets that show their place in a melody. From this point of view, chords are a group of notes which are played at the same moment. For melody generation, the next note or chord must be predicted based on already existed part. It's an example of `seq2seq` problem, and `GRU` model could be used to solve it. For simplicity, note offsets in the code do not show a specific place of a note or a chord in a piece; they show time delay which must pass before the predicted element is played.    

This project shows a simple example of `.mid` files generation. 
To do it a small model based on `GRU` architecture is used to learn 
patterns (order of notes and chords) from existed melodies (see `data` directory).

The project is created from 
[Neuro Platform Project Template](https://github.com/neuromation/cookiecutter-neuro-project)
 and  designed to run on [Neuro Platform](https://neu.ro), 
 so you can jump into problem-solving right away using the instruction from `Quick Start` section.
 
# Quick Start

First of all, register on [Neuro Platform](https://neu.ro) and install `neuro` client:

```
pip install -U neuromation
neuro login
```

This repository already contains pre-trained models, so you can run Jupyter Notebook with inference code and play with them. To do it, copy the following command:

```
make setup && make upload && make jupyter
```

For a deeper understanding of what this command does and the project structure, read the explanation below.

# Development Environment

## Directory structure

| Local directory                      | Description       | Storage URI                                                                  | Environment mounting point |
|:------------------------------------ |:----------------- |:---------------------------------------------------------------------------- |:-------------------------- | 
| `data/`                              | Data              | `storage:midi-generator/data/`                              | `/midi-generator/data/` | 
| `midi-generator/`                    | Directory with code    | `storage:midi-generator/midi-generator/` | `/midi-generator/cmidi-generator/` |
| `notebooks/`                         | Jupyter notebooks | `storage:midi-generator/notebooks/`                         | `/midi-generator/notebooks/` |
| `results/`                           | Logs and results  | `storage:midi-generator/results/`                           | `/midi-generator/results/` |

## How to train your own model or run existed

Follow the instructions below to set up the environment and start development session.

### Log in neuro platform

Before environment setup it's required to login on platform:

`neuro login`

It can be done with `Github` account.

### Setup development environment 
The first thing you need to do is specify environment on `neuro` platform. To do it run this command in the project root
directory:
   
`make setup`

What happens during this command:

* Several files from the local project are uploaded to the platform storage (namely, `requirements.txt`, 
  `apt.txt`, `setup.cfg`).
* A new job is started in our [base environment](https://hub.docker.com/r/neuromation/base). 
* Pip requirements from `requirements.txt` and apt applications from `apt.txt` are installed in this environment.
* The updated environment is saved under a new project-dependent name and is used further on.

After that, the image with the name `neuromation-midi-generator` will be created. To see a list of images 
the followed command can be used:

`neuro image ls`

### Resources uploading \ downloading

Alter develop environment is setup, the next step is upload the repository resources on platform with:

`make upload`

This command will upload all repository directories on platform. To specify what you exactly want 
to upload:

| Command                      | Uploaded directory       | 
|:---------------------------- |:-------------------------| 
| `make upload-code`           | `midi-generator`         | 
| `make upload-data`           | `data`                   |
| `make upload-notebooks`      | `notebooks`              | 
| `make upload-results`        | `results`                | 

**WARNING:** After each local code modification, you need to upload code on the platform to have 
updated code there.

Resources also can be downloaded with `make download*` command.

### Generate a new MIDI file

To generate a new midi file you can generation job on platform:

`make generate`

After the command is executed download result file from the platform `make download-results`. 
The result can be opened with `timidity`. To setup generation parameters modify `generate_config.cfg` file, 
but do not forget to upload it on the platform after modification. 

### Model training

You also can train your own model. To do it use the following command:

`make training CONFIG_NAME=base_train_config.cfg`

To specify model and training parameters modify `base_train_config.cfg` file. 
If you want to change training config, just specify `CONFIG_NAME` variable in the command 
(see `midi-generator/configs` for the full list of available predefined train configs).
Training process can be followed 
with `tensorboard`:

`make tensorboard`

### Developing mode

Remote terminal can be run to execute code manually:

`make developing && connect-developing`

All modified code can be downloaded on a local machine with `make download` command.

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
