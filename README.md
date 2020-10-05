# Converting Data Intended for Django into Markdown Files for GitHub

This little app was written to convert the Django-data for the DHRI's curriculum website into GitHub-ready markdown files.

## Requirements

- [Git](https://git-scm.com)
- [Python 3.8](https://www.python.org/)

---

## Running the Script

### Clone the workshop

First, clone the desired workshop. In the following example, we will work with the `python` workshop. In your terminal, type:

```sh
$ git clone https://www.github.com/DHRI-Curriculum/python
```

Navigate into the newly cloned directory:

```sh
$ cd python
```

### Update Submodule

Register the submodule with your `git` installation:

```sh
$ git submodule init
```

Make sure the submodule is up-to-date:

```sh
$ git submodule update
```

### Run `setup.py`

Run the script using your locally installed version of Python 3. In this example, the `python` command is aliased to `python3` already. You may need to write `python3` instead of `python` here.

_Note that the Python script needs to be run inside the workshop directory itself:_

```sh
$ python localdjango/setup.py
```

This should result in a new `README.md` file and an accompanying `sections` directory with all the markdown files.

_Note that this script also makes all the references to the `images` directory into a relative reference to `../images` directory. You need to manually make sure that that's where the images for your `lessons.md` file lives._
