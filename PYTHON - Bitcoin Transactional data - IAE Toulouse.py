# -*- coding: utf-8 -*-
"""quiz2_solutions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aBfNQ1QgktE8q_l7Drkxx3raW1ul1003

# Quiz 2: Bitcoin blocks


---


**Author:** Christophe Bisière (christophe.bisiere@tsm-education.fr)

**Version:** 2022-10-03


---

This list describes the fields in the dataset (and their unit) provided for this session:

1. `time`:
Block timestamp, as set by the miner
(Datetime, UTC)
1. `height`:
Block height
(Height)
1. `revenue`:
Total revenue collected by the miner, that is, sum of outputs of the coinbase transaction. This is equal to the block reward pocketed by the miner (i.e. new bitcoins created) plus total fees collected by the miner.
(Satoshi)
1. `fee`:
Total fees collected by the miner: sum for all transactions (but excluding the coinbase) of the difference between the total input and total output of the transaction.
(Satoshi)
1. `tx_count`:
Number of transactions in the block (including the coinbase)
(Number)
1. `base_size`:
Size of the part of the block which counts against the 1MB (1 million bytes) block size limit.
(Byte)
1. `input_count`:
Total number of inputs of all transactions in the block
(Number)
1. `input_value`:
Total input value of all transactions in the block
(Satoshi)
1. `output_count`:
Total number of outputs of all transactions in the block (including the coinbase transaction)
(Number)
1. `output_value`:
Total output value of all transactions in the block (including the output of the coinbase transaction)
(Satoshi)
1. `protocol_block_reward`:
Block reward as set by the protocol (note: this value is not stored into the block itself; according to the protocol, a block is considered as invalid if the miner tries to collect more than this value)
(Satoshi)
1. `difficulty`:
Block difficulty
(Difficulty)
"""

# mount my Google Drive on the VM

from google.colab import drive
drive.mount('/gdrive')

#
# Setup
#

import os
from pathlib import Path
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#
# Read the csv file containing block data
#

# where the data file is located
DIR_DATA = "/gdrive/MyDrive/Classroom/UE05 FinTech M2 Finance FIT 2022-2023/data"

bk = pd.read_csv(os.path.join(DIR_DATA, 'blocks_for_FIT_satoshis.csv'), 
                 parse_dates=['time'],
                 nrows=None) # use a number instead of None to read only a few lines

display(bk.dtypes)
bk

"""The table displayed above shows that:

1. There are days over which no blocks have been mined, e.g., 2009-01-04.
2. Some blocks are missing over the last day, as the data collection process over that day seems to have stopped at around 11:00 UTC.

## Data Profiling
"""

import sys
!{sys.executable} -m pip install -U pandas-profiling
!jupyter nbextension enable --py widgetsnbextension

#
# data exploration
#

from pandas_profiling import ProfileReport
profile = ProfileReport(bk, title='Bitcoin block data: Profiling Report', 
                        html={'style':{'full_width':True}})

profile.to_file(output_file=os.path.join(DIR_DATA, 'bitcoin_block_data_profile.html'))

"""## 1) On average, how many blocks are mined per day?  How does it compare to the target block per day given that the target time between two blocks set by the protocol is 10 minutes?

"""

# day part of the timestamp
bk['date'] = bk['time'].dt.date

# first (slightly wrong) solution:
bk[['date']].groupby('date').size().mean()

"""We note that the average number of blocks computed above is likely to be slightly wrong, due to two implicit assumptions:

1. At least one block has been mined per day. We know that this is not true, as in January 2009, a few days have seen no blocks mined at all. These days without any blocks will not be counted in the average, while they should be counted as days with zero blocks mined.
2. All the blocks are available over all the days in the sample. We can assume it to be true for all days but the last one, as we do not know when the block collection process ended. Thus, including the last day in the sample is likely to slightly underestimate the average number of blocks mined per day. 
"""

# second (still slightly wrong) solution, addressing the first issue:
#  {number of blocks} / {number of days}
bk.shape[0]/(bk['date'].max()-bk['date'].min()).days

# third solution, addressing both issues:
#  same as above, but remove the last day
bk_full_days = bk[bk['date'] < bk['date'].max()]
bk_full_days.shape[0]/(bk_full_days['date'].max()-bk_full_days['date'].min()).days

# fourth solution, a bit more complicated:

# create a day index covering the period from the first day 
#  to the day before the last day in the sample
first_date = bk['date'].min()
last_date = bk['date'].max() - pd.Timedelta(days=1)
idx = pd.date_range(start=first_date, end=last_date)

# compute number of blocks per day for days with at least one block
dc = bk[['date']].groupby('date').size()

# reindex and replace NaN with zeros, so as to insert missing dates with zero 
#  blocks mined
dc = dc.reindex(idx, fill_value=0)

avg_blocks_per_day = dc.mean()

TARGET_BLOCKS_PER_DAY = 24*60/10

print("Between {} and {}, {:.2f} blocks have created per day, on average." 
  .format(first_date, last_date, avg_blocks_per_day))
print("This is {} than the target value of {} blocks.".format("less" 
  if avg_blocks_per_day < TARGET_BLOCKS_PER_DAY else "more", TARGET_BLOCKS_PER_DAY))

# visual inspection to check that our daily series has no obvious flaws
dc

"""We note that there the computed average is still subject to the mild implcit assumption that Nakamato started mining on January 3rd, 2009, and not before.

## 2) Compute `new_coins`, the new coins (in satoshis) created by each block.

Actual block reward can be computed either as `revenue - fee` or as `output_value - input_value`.
"""

bk['new_coins'] = bk['revenue'] - bk['fee']

#
# Check that both ways are indeed equivalent (using two alternative syntaxes for 
#  illustrative purpose)
#

# check (syntax 1)
r = bk.query("new_coins != (output_value - input_value)")
if not r.empty:
  print("Check the following blocks:")
  display(r)

# same check (syntax 2)
r = bk[bk['new_coins']!=bk['output_value']-bk['input_value']]
if not r.empty:
  print("Check the following blocks:")
  display(r)

"""## 3) Check whether miners are always collecting the full block reward set by the protocol. """

# unclaimed money supply
bk['coins_burned'] = bk['protocol_block_reward'] - bk['new_coins']

r = bk[bk['coins_burned']>0]
if not r.empty:
  print("{:,} blocks did not collect the full block reward.".format(r.shape[0]))

print("{:,} BTC burned.".format(r['coins_burned'].sum()/1e8))

r

"""## 4) Compute `fee_pct_reward` the fees in proportion of the block reward. Plot the monthly average."""

bk['fee_pct_reward'] = bk['fee'] / bk['revenue'] * 100

pct_fees = bk['fee_pct_reward'].mean()

print("The average percentage of fees per block is {:.2f}%.".format(pct_fees))

#
# plot monthly average
#

title="Fees as % of block total reward (monthly average)"

ax = bk[['time','fee_pct_reward']].set_index('time').resample('M').mean() \
    .plot(figsize=(10, 6), grid=True, title=title, legend=False)
ax.set_ylabel('fees (% of block total reward)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

"""## 5) Compute the percentage of empty blocks. Plot the monthly average.

An empty block is a block containing only the coinbase transaction.
"""

# is a block empty? (i.e. contains only the coinbase)
bk['is_empty'] = bk['tx_count'] == 1

# percentatge of empty blocks
pct_empty = bk['is_empty'].mean() * 100

print("The percentage of empty blocks is {:.2f}%.".format(pct_empty))

#
# plot monthly average proportion of empty blocks
#

title="Empty Bitcoin blocks (monthly average)"

ax = bk[['time','is_empty']].set_index('time').resample('M').mean().multiply(100) \
    .plot(figsize=(10, 6), grid=True, title=title, legend=False)
ax.set_ylabel('empty blocks (%)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())