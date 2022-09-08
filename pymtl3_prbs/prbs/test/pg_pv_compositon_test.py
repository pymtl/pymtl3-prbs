'''
==========================================================================
pg_pv_composition_test.py
==========================================================================
Composition tests for PatterGenerator and PatternVerifier.

Author : Yanghui Ou
  Date : Aug 25, 2022
'''

import pytest

from pymtl3 import *

from ..PatternVerifier import PatternVerifier
from ..PatternGenerator import PatternGenerator
from ...lfsr.LfsrFL  import LfsrFL
from ...utils import gen_bitmap_std, gen_bitmap_ahd

#-------------------------------------------------------------------------
# Local parameters
#-------------------------------------------------------------------------

prbs7_poly = 'x^7 + x^6 + 1'
seed       = 97

#-------------------------------------------------------------------------
# PgPvComposition
#-------------------------------------------------------------------------

class PgPvComposition( Component ):
  def construct( s, nbits, lfsr_bitmap ):

    # Local parameters

    s.T = mk_bits( nbits )

    # Interface

    s.seed = InPort( s.T )

    s.pg_en           = InPort()
    s.pg_insert_error = InPort()

    s.pv_en           = InPort()
    s.pv_locked       = OutPort()
    s.pv_error_count  = OutPort(32)

    # Components

    s.pg = PatternGenerator( nbits, lfsr_bitmap )
    s.pv = PatternVerifier ( nbits, lfsr_bitmap )

    # Connections

    s.seed //= s.pg.seed

    s.pg_en           //= s.pg.en
    s.pg_insert_error //= s.pg.insert_error

    s.pv_en           //= s.pv.en
    s.pv_locked       //= s.pv.locked
    s.pv_error_count  //= s.pv.error_count

    s.pg.out //= s.pv.in_

  def line_trace( s ):
    return f'{s.pg.line_trace()}->{s.pv.line_trace()}'

#-------------------------------------------------------------------------
# test_sanity_check
#-------------------------------------------------------------------------

def test_sanity_check():
  ahd_bmap = gen_bitmap_ahd( 32, prbs7_poly )
  dut = PgPvComposition( 32, ahd_bmap )
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test_nbit
#-------------------------------------------------------------------------

@pytest.mark.parametrize( 'nbits', [8, 10, 16, 32] )
def test_nbit( nbits, cmdline_opts ):
  ahd_bmap = gen_bitmap_ahd( nbits, prbs7_poly )
  dut = PgPvComposition( nbits, ahd_bmap )
  dut.apply( DefaultPassGroup(linetrace=True) )

  dut.seed            @= seed
  dut.pg_en           @= 0
  dut.pv_en           @= 0
  dut.pg_insert_error @= 0
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

  dut.pv_en @= 1
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()

  dut.pg_en @= 1
  dut.sim_tick()

  for _ in range( 500 ):
    dut.sim_tick()

  assert dut.pv_locked
  assert dut.pv_error_count == 0

