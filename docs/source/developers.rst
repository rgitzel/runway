.. _developers:

Developers
==========

Want to work on the Runway code itself?

The simplest way to get started is to modify the source code in place while working on an existing project.

Running the following command from your Runway project folder will check out out the current code
and then will configure ``pipenv`` to use that code::

    $ pipenv install -e git+https://github.com/onicagroup/runway#egg=runway

(Or, if you have your own fork, replace ``onicagroup`` appropriately.)

Where is the code? This will give you the root folder::

    $ pipenv --venv
    /Users/myname/.local/share/virtualenvs/my-project-name-d7VNcTay

From there look in ``src/runway/runway``.

Whatever changes you make to the files there will be reflected when you run Runway
using ``pipenv`` in the project folder.



Compiling the code
^^^^^^^^^^^^^^^^^^

Once you have made changes you are happy with, you should test and lint the changes.

If you have a Python environment locally, then `make test` should do the trick::

    $ make test
    sed '/^\[!\[Build Status\]/d' README.md | pandoc --from=markdown --to=rst --output=README.rst
    python setup.py test
    running test
    ....
    ------------------------------------
    Your code has been rated at 10.00/10

The first time you run this it might take awhile while the dependencies are downloaded.


Compiling the code with Docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't have (or don't want) a local Python build environment for Runway, then you can use this Dockerfile::

    FROM python:3

    RUN apt-get update && apt-get install -y pandoc

    RUN pip3 install flake8 ply pylint

    VOLUME /src

    CMD cd /src; bash

Build an image from the file, then invoke it from the root of the checked-out repo::

    $ docker build . -t runway-builder
    ...

    $ docker run -it -v $(pwd):/src runway-builder
    ....
    ------------------------------------
    Your code has been rated at 10.00/10


Ideally you'll see this success message at the end.

As above, this will take awhile the first time you run it.  Dependencies should end up in the `.egg` folder
in the repository root, so it will persist beyond the Docker container.







