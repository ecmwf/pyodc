Welcome to pyodc’s documentation!
=================================

.. warning::
   This documentation is a work in progress. It is not yet considered ready.

**pyodc** is a Python interface to `odc`_ for encoding/decoding ODB-2 files.

The package contains two different implementations of the same library:

.. index:: pyodc

* **pyodc** is a pure Python encoder and decoder for ODB-2 data, which encodes data from, and decodes it into pandas data frames

.. index:: codc

* **codc** is an implementation of the same API as **pyodc** that depends on the ECMWF **odc** library, and comes with *much* better performance

.. index:: Contents

.. toctree::
   :maxdepth: 2
   :caption: Contents

   content/introduction
   content/installation
   content/usage
   content/api
   content/development
   content/licence
   genindex


.. _`odc`: https://github.com/ecmwf/odc
