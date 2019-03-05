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








