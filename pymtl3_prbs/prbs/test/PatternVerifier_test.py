'''
==========================================================================
PatternVerifier_test.py
==========================================================================
Unit tests for PatternVerifier.

Author : Yanghui Ou
  Date : Aug 25, 2022
'''

import pytest

from pymtl3 import *

from ..PatternVerifier import PatternVerifier
from ...lfsr.LfsrFL import LfsrFL
from ...utils import gen_bitmap_std, gen_bitmap_ahd

#-------------------------------------------------------------------------
# Local parameters
#-------------------------------------------------------------------------

prbs7_poly = 'x^7 + x^6 + 1'
seed       = 97

#-------------------------------------------------------------------------
# test_sanity_check
#-------------------------------------------------------------------------

def test_sanity_check():
  ahd_bmap = gen_bitmap_ahd( 32, prbs7_poly )
  dut = PatternVerifier( 32, ahd_bmap )
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
  ref      = LfsrFL( ahd_bmap )
  dut      = PatternVerifier( nbits, ahd_bmap )
  dut.apply( DefaultPassGroup(linetrace=True) )

  dut.en   @= 0
  dut.in_  @= seed
  dut.sim_reset()

  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()
  dut.en @= 1

  ref_curr = seed
  for _ in range( 500 ):
    ref_curr = ref.get_next( ref_curr )
    dut.in_ @= ref_curr
    dut.sim_tick()

  assert dut.locked
  assert dut.error_count == 0

  # Insert error
  dut.in_ @= 0
  dut.sim_tick()
  dut.sim_tick() # once extra cycle since input is registered

  assert ~dut.locked
  assert dut.error_count == 1

  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()

