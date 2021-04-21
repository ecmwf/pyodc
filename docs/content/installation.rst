Installation
============

Dependencies
------------

.. index:: Dependencies

Required
^^^^^^^^

.. index::
   single: Dependencies; Required

* Python (3/3.5/3.6/3.7)


Optional
^^^^^^^^

.. index:: Dependencies; Optional

* `odc`_ (>= 1.3.0)
* `Jupyter Notebook`_

.. note::

   In order for **codc** to work, the **odc** library must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library.


.. _`odc`: https://github.com/ecmwf/odc
.. _`Jupyter Notebook`: https://jupyter.org


Python Package Installer
------------------------

.. index:: Installation
   single: Installation; PIP

Install the package via PIP:

.. code-block:: shell

   pip install pyodc

Check if the module was installed correctly:

.. code-block:: shell

    python
    >>> import pyodc
    >>> import codc # optional


Conda Forge
-----------

.. index::
   single: Installation; Conda

.. todo::

   First make sure the **pyodc** package is available through Conda.
