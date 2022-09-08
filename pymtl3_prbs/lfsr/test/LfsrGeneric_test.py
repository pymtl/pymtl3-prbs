'''
==========================================================================
LfsrGeneric_test.py
==========================================================================
Unit tests for LfsrGeneric.

Author : Yanghui Ou
  Date : Aug 23, 2022
'''

import pytest

from pymtl3 import *

from ..LfsrGeneric import LfsrGeneric
from ..LfsrFL import LfsrFL
from ..utils import gen_bitmap_std, gen_bitmap_ahd

#-------------------------------------------------------------------------
# Local parameters
#-------------------------------------------------------------------------

prbs7_poly = 'x^7 + x^6 + 1'
seed       = 97

#-------------------------------------------------------------------------
# test_rtl_vs_fl
#-------------------------------------------------------------------------

def test_sanity_check():
  ahd_bmap = gen_bitmap_ahd( 8, prbs7_poly )
  dut = LfsrGeneric( 8, ahd_bmap )
  ref = LfsrFL( ahd_bmap )

  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()


@pytest.mark.parametrize( 'nbits', [8, 10, 16, 32] )
def test_nbits( nbits ):
  ahd_bmap = gen_bitmap_ahd( nbits, prbs7_poly )
  dut = LfsrGeneric( nbits, ahd_bmap )
  ref = LfsrFL( ahd_bmap )

  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()

  dut.in_ @= seed
  dut.sim_tick()
  ref_curr = ref.get_next( seed )

  assert dut.out == ref_curr

  for i in range( 100 ):
    dut.in_ @= dut.out
    dut.sim_tick()
    ref_curr = ref.get_next( ref_curr )
    assert dut.out == ref_curr, f'failed at {i}-th iteration: {dut.out} (dut) =! {ref_curr} (ref)'

