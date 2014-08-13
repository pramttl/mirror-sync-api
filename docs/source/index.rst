.. Mirror Syncing API - OSU | Open Source Lab documentation master file, created by
   sphinx-quickstart on Tue Aug 12 00:05:36 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mirror Syncing API documentation!
============================================

Mirror Syncing API is a project that provides a better design for periodic mirror
syncing of projects from upstream rsync sources.

The OSL hosts a three-node FTP  mirroring cluster to host various projects.
The architecture for mirror syncing at OSL contains a single master machine that
syncs from upstream and then triggers 3 slave hosts to sync from it.
With various upstream projects to manage and a lot of configuration files, bash
scripts and crontab entries for periodic scheduling, the management of several
FTP Mirror’s (ie. several upstream projects) is a complicated task. Some of the
import problems that this API aims at solving is.

0. Easy to query and modify syncing period of existing projects.
1. Ability to retrieve information of projects scheduled for syncing.
2. No need to edit crontab entries ever again.
3. Bi-directional communication between master and slave that enables taking feedback from slaves.

Assumptions:

0. This API assumes that there is a setup where upstream projects are to be synced from rsync sources.
1. Master/Slave syncing architecture is assumed. There can be 0 or more slaves.
   Using a slave node as an ftp host is optional but as many of them can be added
   easily via the api.
2. Project names must be unique. To run an architecture with slave nodes, master
   node must run an rsync daemon with only one module in the configuration file.

.. _cli: https://github.com/pramttl/mirror-sync-cli


Installation
------------
.. toctree:
    :maxdepth: 1

    installation

Design
------
.. toctree::
    :maxdepth: 1

    desgin/architecture

Usage
------
.. toctree::
    :maxdepth: 1

    usage/api


Development
-----------


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

