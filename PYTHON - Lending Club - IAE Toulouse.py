# -*- coding: utf-8 -*-

Automatically generated by Colaboratory.


Author: thi-thanh-mai.bui@tsm-education.fr
Date: 2022/11/01



Original file is located at
    https://colab.research.google.com/drive/1ZYSUkjh_0cgEc0BjlHBdP6VrGfLUUTD4
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

# normalize figure size
plt.rcParams['figure.figsize'] = (10.0, 6.0)

# always show all the columns of a dataframe
pd.set_option('display.max_columns', None)

#
# Read the csv file containing Lending Club data, Q4 2018
#

DIR_DATA = "/gdrive/MyDrive/Classroom/UE05 FinTech M2 Finance FIT 2022-2023/data"

filename = os.path.join(DIR_DATA, 'LoanStats_2018Q4.csv')

# columns of interest
usecols = [
  'loan_amnt',
  '#DIV/0!',
  'int_rate',
  'grade',
  'sub_grade',
  'home_ownership',
  'annual_inc',
  'tot_cur_bal',
  'delinq_2yrs',
  'title'
]

# read the file: column names are in the second row
df = pd.read_csv(filename, skiprows=1, usecols=usecols, skipfooter=4, 
                 engine='python', nrows=None)

display(df.dtypes)
df

"""# Quiz 4: P2P lending


---


**Author:** Christophe Bisière (christophe.bisiere@tsm-education.fr)

**Version:** 2022-11-18


---

During this session, you will work on Lending Club data (Q4 2018).

The data dictionary is available here:
https://www.kaggle.com/jonchan2003/lending-club-data-dictionary


"""

#
# prepare data
#

# fix column name
df.rename(columns={'#DIV/0!':'duration_months'}, inplace=True)

# filter out empty rows
df.dropna(how='all', inplace=True)

# extract interest rate using a regexp
df['rate'] = df['int_rate'].str.extract('([0-9]+\.[0-9]+)\%').astype(float)

df

"""## 1)​ Use the data profiling tool pandas-profiling to conduct an exploratory data analysis

https://github.com/pandas-profiling/pandas-profiling

"""

import sys
!{sys.executable} -m pip install -U pandas-profiling
!jupyter nbextension enable --py widgetsnbextension

#
# data exploration
#

from pandas_profiling import ProfileReport
profile = ProfileReport(df, title='Lending Club data (Q4 2018): Profiling Report', 
                        html={'style':{'full_width':True}})
#profile.to_notebook_iframe()
profile.to_file(output_file=os.path.join(DIR_DATA, 'lending_club_data_profile.html'))

"""## 2)​ ​ Compute the following statistics:

* Average loan size (USD)
* Average maturity (months)
* Average interest rate (%)
* Average income borrower (USD)
* Average total loan balance borrower (USD)
* Average number of delinquencies in the past 2 years
* Home ownership types in % 
* Loan motives in %

"""

#
# requested stats
#

print("• Average loan size ($): {:,.0f}".format(df['loan_amnt'].mean()))
print("• Average maturity (months): {:.2f}".format(df['duration_months'].mean()))
print("• Average interest rate (%): {:.2f}".format(df['rate'].mean()))
print("• Average income borrower ($): {:,.0f}".format(df['annual_inc'].mean()))
print("• Average total loan balance borrower ($): {:,.0f}".format(df['tot_cur_bal'].mean()))
print("• Average number of delinquencies in the past 2 years: {:.2f}".format(df['delinq_2yrs'].mean()))
print("• Home ownership types in %:")
print(df['home_ownership'].value_counts(normalize=True)*100)
print("• Loan motives in %:")
print(df['title'].value_counts(normalize=True)*100)

"""## 3) Compute a few additional statistics or graph you find interesting"""

#
# Grades
#

plt.title("Grades on loan applications\n(Lending Club, Q4 2018)")

ax = df['grade'].value_counts(normalize=True).plot.bar(rot=0)
ax.grid(axis='y')
ax.set_xlabel('Grade')
ax.set_ylabel('Frequency')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0,decimals=0));

#
# Delinquencies
#

plt.title("Delinquencies in the past 2 years on loan applications\n(Lending Club, Q4 2018)")

ax = df['delinq_2yrs'].value_counts(normalize=True).plot.bar(rot=0)
ax.grid(axis='y')
ax.set_xlabel('Number of delinquencies in the past 2 years')
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f'))
ax.set_ylabel('Frequency')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0,decimals=0));

#
# Average interest rate by number of delinquencies in the past 2 years
#

ax = df.groupby('delinq_2yrs').agg({'rate': 'mean'}).plot.bar(rot=0)
ax.grid(axis='y')
ax.set_xlabel('Number of delinquencies in the past 2 years')
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f'))
ax.set_ylabel('Rate of interest')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1));

