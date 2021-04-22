Installation
============

.. index:: Dependencies

Dependencies
------------

.. index::
   single: Dependencies; Required

Required
^^^^^^^^

* Python (3/3.5/3.6/3.7)


.. index:: Dependencies; Optional

Optional
^^^^^^^^

* `odc`_ (>= 1.3.0)
* `Jupyter Notebook`_

.. note::

   In order for **codc** to work, the **odc** library must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library.


.. _`odc`: https://github.com/ecmwf/odc
.. _`Jupyter Notebook`: https://jupyter.org


.. index:: Installation
   single: Installation; PIP

Python Package Installer
------------------------

Install the package via PIP:

.. code-block:: shell

   pip install pyodc

Check if the module was installed correctly:

.. code-block:: shell

    python
    >>> import pyodc
    >>> import codc # optional


.. index::
   single: Installation; Conda

Conda Forge
-----------

.. todo::

   **pyodc** package is not available through Conda yet.
