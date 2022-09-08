'''
==========================================================================
LfsrGeneric.py
==========================================================================
Generate an RTL LFSR instance based on input bitmap.

Author : Yanghui Ou
  Date : Sep 6, 2022
'''

from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Reg

#-------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------
# Returns the max order of the bitmap

def _max_order( bitmap ):
  ...

# Returns the number of ones in each row
def _num_terms( bitmap ):
  ...

#-------------------------------------------------------------------------
# LfsrGeneric
#-------------------------------------------------------------------------

class LfsrGeneric( Component ):

  def construct( s, nbits, bitmap ):

    # Checks

    assert nbits == len( bitmap ), f'invalid bitmap for {nbits}-bit'

    # Local parameter

    s.nbits = nbits
    s.T     = mk_bits( nbits )

    # Interface

    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

    # Wires
    # TODO: optimize the maxtrix size based on max order?
    s.xor_in = [ Wire( nbits ) for _ in range( nbits ) ]

    # Components

    s.lfsr = Reg( s.T )

    # Connections

    s.lfsr.in_ //= s.in_

    # Xor input based on bitmap
    for i, expr in enumerate( bitmap ):
      for j, term in enumerate( expr ):
        if term:
          s.xor_in[i][j] //= s.lfsr.out[j]
        else:
          s.xor_in[i][j] //= b1(0)

    # Logic

    @update
    def up_out():
      for i in range( nbits ):
        s.out[i] @= reduce_xor( s.xor_in[i] )

  def line_trace( s ):
    return f'{s.in_}({s.lfsr.out}){s.out}'

