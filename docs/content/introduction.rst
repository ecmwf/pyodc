Introduction
============

.. index:: Introduction

ODB-2 is a compact data format suited for storage, transmission and archival of meteorological observation data in a tabular format, with each row corresponding to one observation. Observation is self-describing and can come from many different data sources and many types of instrument.

**pyodc** provides a thin encoder and decoder to make ODB-2 data available for the **pandas** or **numpy** ecosystem. In addition to that, it also has an interface to explore the metadata without actually decoding ODB-2 data.


ODB-2 Format Overview
---------------------

.. index:: ODB-2
   single: ODB-2; Format
   single: ODB-2; Frame
   single: ODB-2; Header

An ODB-2 data stream is comprised of a sequence of frames. Each frame encodes a table of data, described by a header.

.. figure:: /_static/odb-2-message-stream.svg
   :alt: ODB-2 Data Structure

   ODB-2 Data Structure


It is important to understand that the ODB-2 should not be considered as a file format, but a data stream instead. In a stream of messages frames can also be unrelated, having entirely different data, so they must be decoded separately. However, if in a stream of messages the frames contain the the same data types, they are suitable for combined decoding and processing.
