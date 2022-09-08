'''
==========================================================================
PatternGenerator.py
==========================================================================
RTL implemetation for PRBS generator.
Value of LFSR will be updated only if s.en is 1.
If s.insert_error is 1, then the LSB of the output is inverted.

Author : Yanghui Ou
  Date : Aug 24, 2022
'''

from pymtl3 import *

from ..lfsr import LfsrGeneric

#-------------------------------------------------------------------------
# PatternGenerator
#-------------------------------------------------------------------------

class PatternGenerator( Component ):
  def construct( s, nbits, lfsr_bmap ):

    # Local parameters

    s.T = mk_bits( nbits )

    # Interface

    s.seed = InPort ( s.T )
    s.out  = OutPort( s.T )

    s.en           = InPort()
    s.insert_error = InPort()

    # Wires and registers

    s.in_r = Wire( s.T )

    # Components

    s.lfsr = LfsrGeneric( nbits, lfsr_bmap )

    # Connections and assignments

    s.lfsr.in_ //= lambda: s.lfsr.out if s.en else s.seed

    # Logic

    @update
    def up_out():
      s.out    @= s.lfsr.out
      s.out[0] @= s.insert_error ^ s.lfsr.out[0]

    @update_ff
    def up_in_r():
      if s.reset:
        s.in_r <<= s.seed
      else:
        s.in_r <<= s.in_r

  def  line_trace( s ):
    en = ' ' if s.en else '#'
    return f'({en}<{s.seed}>){s.out}'

