Development
===========

.. index:: Github

Contributions
-------------

The code repository is hosted on `Github`_, feel free to fork it and submit your PRs against the **develop** branch. To clone the repository locally, you can use the following command:

.. code-block:: shell

   git clone --branch develop git@github.com:ecmwf/pyodc.git


Development Dependencies
------------------------

.. index:: Dependencies; Development

Python Packages
^^^^^^^^^^^^^^^

* `cffi`_ (>= 1.14.5)
* `pandas`_ (>= 1.2.3)
* `pytest`_ (>= 6.2.3)


Shared Libraries
^^^^^^^^^^^^^^^^

* `odc`_ (>= 1.3.0)


Converters
^^^^^^^^^^

* `pandoc`_ (>= 2.13)


.. index:: Unit Tests

Run Unit Tests
--------------

To run the test suite, you can use the following command:

.. code-block:: shell

   python -m pytest


Build Documentation
-------------------

To build the documentation locally, please install the Python dependencies first:

.. code-block:: shell

   cd docs
   pip install -r requirements.txt
   make html

The built HTML documentation will be available under the ``docs/_build/html/index.html`` path.


.. _`Github`: https://github.com/ecmwf/pyodc
.. _`cffi`: https://cffi.readthedocs.io
.. _`pandas`: https://pandas.pydata.org/
.. _`pytest`: https://pytest.org
.. _`odc`: https://github.com/ecmwf/odc
.. _`pandoc`: https://pandoc.org
