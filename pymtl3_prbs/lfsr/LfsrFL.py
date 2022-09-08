'''
==========================================================================
LfsrFL.py
==========================================================================
Functional level model for LFSR.

Author : Yanghui Ou
  Date : Sep 5, 2022
'''

from pymtl3 import *

#-------------------------------------------------------------------------
# LfsrFL
#-------------------------------------------------------------------------

class LfsrFL:

  def __init__( s, bitmap ):
    s.nbits  = len( bitmap )
    s.T      = mk_bits( s.nbits )
    s.bitmap = bitmap

  def get_next( s, in_ ):
    tmp     = s.T()
    bits_in = s.T( in_ )

    for i, bitstream in enumerate( s.bitmap ):
      for j, term in enumerate( bitstream ):
        if term:
          tmp[i] ^= bits_in[j]

    return tmp

