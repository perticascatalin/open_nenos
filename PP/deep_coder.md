# Deep Coder

[Link](https://openreview.net/pdf?id=ByldLrqlx)

Topic: **Program Synthesis**

## What this paper is about?

A method of using neural networks to predict the probability that certain functions (from DSL) appear in a program satisfying a set of given input-output constraints. These probabilities are then used to optimize the search for the program satisfying the input-output constraints.

## DSL

### First Order Functions

Head, Last, Take, Drop, ...

### Higher Order Functions

Map, Filter, ...

## Neural Networks

- M input-output examples used as input for the network
- network outputs predictions for program attributes (probability that a function from the DSL will appear in the program)

## Search