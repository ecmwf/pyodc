Installation
============

.. index:: Dependencies

Dependencies
------------

.. index::
   single: Dependencies; Required

Required
^^^^^^^^

* Python 3.x


.. index:: Dependencies; Optional

Optional
^^^^^^^^

* `odc`_ (>= 1.4.0)
* `Jupyter Notebook`_

.. note::

   For **codc** to work, the **odc** library must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library. There are multiple ways to make the library visible to CFFI: it can be installed as a system library, the installation prefix can be passed in ``odc_DIR`` environment variable, or the library directory can be included in ``LD_LIBRARY_PATH``.


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
