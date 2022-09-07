.. image:: docs/images/squonk2-admin-logo.png

#############
Squonk2 Admin
#############

**SquAd** (Squonk2 Administration) is s Textual-UI (TUI) for the
visualisation and administration of Squonk2 environments. **SquAd** is
designed to be used by those with Squonk2 administrative privileges,
it's of little use to users who are not administrators.

.. image:: docs/images/screenshot.png

**SquAd** uses the `squonk2-python-client`_ to interact with a Squonk2 environment
and uses Will McGugan's `textual`_ framework to provide the user with a simple,
text-based user interface modelled on the popular `k9s`_ Kubernetes monitor.
At the moment **SquAd** is provides non-destructive, *read-only* access to the
chosen Squonk2 environment.

**SquAd** is *NOT* an alternative to (or replacement for) the existing
`Data Manager UI`_. The role of **SquAd** is to provide a simple and lightweight
Data Manager (and Account Server) *monitor*, with administrator-only
features not available in the UI.

*Importantly* **SquAd** should be a "rapid development" platform where we
can add features quickly using a lightweight display framework.
**SquAd** fails if we spend too much time battling with the UI.

We chose `Textual`_ because it...

- has had some favorable reviews
- works
- is extremely lightweight
- is under active development

.. _data manager ui: https://github.com/InformaticsMatters/mini-apps-data-tier-ui
.. _k9s: https://k9scli.io
.. _squonk2-python-client: https://github.com/InformaticsMatters/squonk2-python-client
.. _textual: https://github.com/Textualize/textual

************
Installation
************

**SquAd** is a Python application, written with Python 3.10 and published
to `PyPI`_ and is easily installed using ``pip``::

    pip install im-squad

.. _pypi: https://pypi.org/project/im-squad/

*********
Execution
*********

Before running **SquAd** you must have access to a Squonk2 environment.
**SquAd** obtains details of the environment through a YAML-based
*environments* file. An example file, ``environments``, is located in the root
of this project:

..  code-block:: yaml

    ---
    # An example SquAd environments file.
    #
    # It provides all the connection details for one or more Squonk2 environments.
    # It is expected to be found in the user's home directory
    # as '~/.squad/environments' or the user can 'point' to it by setting
    # 'SQUAD_ENVIRONMENT_FILE', e.g. 'export SQUAD_ENVIRONMENT_FILE=~/my-env'

    # The 'environments' block defines one or more environments.
    # Each has a name. Here we define an environment called 'site-a'
    # but environments can be called anything YAML accepts as a key,
    # although it would aid consistency if you restrict your names to letters
    # and hyphens.
    environments:
      site-a:
        # The hostname of the keycloak server, without a 'http' prefix
        # and without a '/auth' suffix.
        keycloak-hostname: example.com
        # The realm name used for the Squonk2 environment.
        keycloak-realm: squonk2
        # The Keycloak client IDs of the Account Server and Data Manager.
        # The Account Server client ID is optional.
        keycloak-as-client-id: account-server-api
        keycloak-dm-client-id: data-manager-api
        # The hostnames of the Account Server and Data Manager APIs,
        # without a 'http' prefix and without an 'api' suffix.
        # If you have not provided an Account Server client ID its
        # hostname value is not required.
        as-hostname: as.example.com
        dm-hostname: dm.example.com
        # The username and password of an admin user that has access
        # to the Account Server and Data Manager.
        # The user *MUST* have admin rights.
        admin-user: dlister
        admin-password: blob1234

    # The final part of the file is a 'default' property,
    # which SquAd uses to select the an environment from the block above
    # when all else fails. It's simply the name of one of the environment
    # declarations above.
    default: site-a

When **SquAd** starts it will look for the environments file in your home
directory, in the file ``~/.squonk2/environments``. If you place your populated
environments file there you need do nothing else prior to running **SquAd**.
If you prefer to put your ``environments`` file elsewhere, or have multiple
files, set the path to your file using the environment variable
``SQUONK2_ENVIRONMENTS_FILE``::

    export SQUONK2_ENVIRONMENTS_FILE=~/my-squonk2-environments

With an environments file in place you can run **SquAd**::

    squad

As an alternative to having separate ``environments`` files for each Squonk2
environment, you can populate the file with the details of more than one
Squonk2 environment, giving each a unique name. If you do this
you can select them when you launch **SquAd** by providing the
the name of the environment on the command-line.

For example, if you have an ``environments`` file with details of two
environments called ``site-a`` and ``site-b`` you can run **SquAd** with
the command::

    squad site-a

or::

    squad site-b

One environment has be be named in the ``environments`` ``deafult`` property
(maybe your *go to* environment) but using this technique you can quickly
switch between environments, or have multiple **SquAd** applications running,
using a single file.

Logging
-------

You can enable logging from **SquAd** and the underlying textual framework by
setting the environment variable ``SQUONK2_LOGFILE`` when running the
application::

    SQUONK2_LOGFILE=./squad.log squad

Debugging
---------

`Textual`_ doesn't like anything being written to the console so printing
(even to ``stderr``) will topple the display. That's why ``stderr`` is
diverted when the application is running and nothing is printed.
There comes a time, though, when you need to see the error log.
For these times you can run **SquAd** without stderr diverted::

    squad --enable-stderr
