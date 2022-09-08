'''
==========================================================================
PatternGenerator_test.py
==========================================================================
Unit tests for PatternGenerator.

Author : Yanghui Ou
  Date : Aug 24, 2022
'''

import pytest

from pymtl3 import *

from ..PatternGenerator import PatternGenerator
from ...lfsr import LfsrFL
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
  dut = PatternGenerator( 32, ahd_bmap )
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
  dut      = PatternGenerator( nbits, ahd_bmap )
  dut.apply( DefaultPassGroup(linetrace=True) )

  dut.seed         @= seed
  dut.en           @= 0
  dut.insert_error @= 0
  dut.sim_reset()

  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()
  dut.en @= 1

  ref_curr = seed
  for _ in range( 500 ):
    ref_curr  = ref.get_next( ref_curr )
    assert dut.out == ref_curr
    dut.sim_tick()

#-------------------------------------------------------------------------
# test_error
#-------------------------------------------------------------------------

@pytest.mark.parametrize( 'nbits', [8, 10, 16, 32] )
def test_insert_error( nbits, cmdline_opts ):
  ahd_bmap = gen_bitmap_ahd( nbits, prbs7_poly )
  ref      = LfsrFL( ahd_bmap )
  dut      = PatternGenerator( nbits, ahd_bmap )
  dut.apply( DefaultPassGroup(linetrace=True) )

  dut.seed         @= seed
  dut.en           @= 0
  dut.insert_error @= 0
  dut.sim_reset()

  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()
  dut.en @= 1

  ref_curr = seed
  for _ in range( 200 ):
    ref_curr = ref.get_next( ref_curr )
    assert dut.out == ref_curr
    dut.sim_tick()

  dut.insert_error @= 1
  dut.sim_eval_combinational()

  for _ in range( 100 ):
    ref_curr = ref.get_next( ref_curr )
    assert dut.out != ref_curr
    dut.sim_tick()

