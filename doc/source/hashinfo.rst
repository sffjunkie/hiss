Hashing Support
===============

When sending a message to a target if the target is remote then proof that a
password is known by the source is required to be sent. This is peformed by
computing a hash of the password and a salt. Within Hiss this data is
recorded in the the HashInfo class and the hash calculations are provided by
the :meth:`~hiss.hash.generate_hash` function and validated by the
:meth:`~hiss.hash.validate_hash` function.

HashInfo
~~~~~~~~

.. autoclass:: hiss.hash.HashInfo
   :members:
   :private-members:

.. automethod:: hiss.hash.generate_hash

.. automethod:: hiss.hash.validate_hash

