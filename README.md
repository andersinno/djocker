# djocker

Docker tools with a Django twist.

## Requirements

djocker requires Python 3.4 or later.

## How to install?

As simple as `pip install djocker`

## How to use it?

### `dockerize`

The `dockerize` command creates a docker setup for a new or existing project.


### `manage_with_compose`

Run management commands inside the main application container.


## FAQ

**Is this only for creating Ubuntu setups?**

Currently yes, but the code is written to be easily extendable to other operating systems/base images.
The reason for using Ubuntu is that this what a requirement in the beginning of this project.

**Is this only for Python?**

Currenty only Python related questions are supported yes. This can and most likely will
be extended in the future to support more languages.

**Why is Python 3 only for running the scripts?**

While djocker can generate Docker setups for Python 2.7, Python 3 is required to run the scripts for two reasons.
The first and most important one is to force people to use Python 3 as Python 2 should be left to die. The second
one is development speed, if one does not have to worry about compatibility with version 2 then the development
goes smoother as well.
