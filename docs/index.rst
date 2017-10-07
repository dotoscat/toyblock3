.. toyblock3 documentation master file, created by
   sphinx-quickstart on Tue Oct  3 20:41:06 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to toyblock3's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. autofunction:: toyblock3.system

.. autoclass:: toyblock3.System
    :members:
    :special-members: __call__

.. autoclass:: toyblock3.InstanceBuilder
    :members:

.. autofunction:: toyblock3.build_Entity

.. py:class:: toyblock3.Entity
    
    Pool of :class:`Entity` instances.
        
    You can access to any instance defined for this Entity.
    Each Entity are different from each other but they have the same interface.

    .. py:staticmethod:: get
    
        Return an unused instance from its pool and add it to the systems.

    .. py:staticmethod:: components
    
        You can access to any instance's defined for this Entity.
        Each Entity are different from each other but they have the same interface.
        
    .. py:method:: free
    
        Free this entity returning it to its pool and remove it from the systems.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
