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

It will ask you to log in on Neuro Platform when the command is run for the first time. A Github account can be used for this purpose.

This repository already contains pre-trained models, so that you can run Jupyter Notebook with inference code and play with these models. To do so, just copy the following command:

```
make setup && make upload-all && make jupyter
```
