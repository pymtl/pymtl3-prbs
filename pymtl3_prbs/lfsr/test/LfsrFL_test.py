'''
==========================================================================
LfsrFL_test.py
==========================================================================
Unit tests for LfsrFL.

Author : Yanghui Ou
  Date : Sep 5, 2022
'''

import pytest

from pymtl3 import *

from ..LfsrFL import LfsrFL
from ..utils import gen_bitmap_std, gen_bitmap_ahd

#-------------------------------------------------------------------------
# Local parameters
#-------------------------------------------------------------------------

prbs7_poly = 'x^7 + x^6 + 1'
seed       = 97

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( 'nbits', [8, 10, 16, 32] )
def test_prbs7_std( nbits ):
  bmap = gen_bitmap_std( nbits, prbs7_poly )
  dut = LfsrFL( bmap )

  # Warm-up
  curr = dut.get_next( seed )
  for _ in range( nbits):
    curr = dut.get_next( curr )

  # Test
  seq   = [ curr ]
  count = 1
  print()
  while True:
    print( f'{count:3}: {curr}' )
    curr = dut.get_next( curr )
    if curr == seq[0]:
      break
    assert not curr in seq
    seq.append( curr )
    count += 1

  assert count == 127


@pytest.mark.parametrize( 'nbits', [8, 10, 16, 32] )
def test_prbs7_ahd( nbits ):
  bmap = gen_bitmap_ahd( nbits, prbs7_poly )
  dut = LfsrFL( bmap )

  # Warm-up
  curr = dut.get_next( seed )
  for _ in range( nbits ):
    curr = dut.get_next( seed )

  # Test
  seq   = [ curr ]
  count = 1
  print()
  while True:
    print( f'{count:3}: {curr}' )
    curr = dut.get_next( curr )
    if curr == seq[0]:
      break
    assert not curr in seq
    seq.append( curr )
    count += 1

  assert count == 127
