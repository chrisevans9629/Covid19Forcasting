
# %%
import pandas as pd

print('could not find daily cases files.  regenerating...')
data = pd.read_csv('covid_confirmed_usafacts.csv')
# convert column wide to rows
data = data.melt(id_vars=["countyFIPS","County Name", "State", "StateFIPS"], var_name="date", value_name="value")
print(data.head(4))

# %%

# select columns
data = data[['countyFIPS','value','date', 'County Name', 'State']]

data['date'] = pd.to_datetime(data['date'])

# rename columns
data = data.rename(columns={"countyFIPS": "fips", "value": "act_cases", "County Name": "county", "State": "state"})

print(data.head(10))

# %%
# Validate the data

test_data = data[(data.date >= '2020-09-05') & (data.date <= '2020-09-12')]

test_data = test_data.groupby(['date']).sum()

# the difference between the max and min should be 230k
print(test_data.head(100))
print(test_data['act_cases'].max() - test_data['act_cases'].min())



# %%
# get date from a week ago
data['date_last_week'] = data['date'] - pd.to_timedelta(7, unit='d')

data.head(10)

# %%

#for each county merge the act_cases with itself
data1 = data
data2 = data

print('count: ', len(data))

result = pd.merge(data1, data2, how='left', suffixes=['','_last_week'], left_on=['date_last_week','fips','state'], right_on=['date','fips','state'])

print('count: ', len(data))

result['weekly_cases'] = result['act_cases'] - result['act_cases_last_week']

# %%


# %%
# Allocate fips 0 accross counties

# state_county_count = result[result.fips != 0].groupby('state').count()[['fips']].reset_index().rename(columns={"fips": "counties"})
# state_unallocated = result[result.fips == 0].groupby(['state', 'date']).sum()[['weekly_cases']].reset_index()

# state_unallocated[state_unallocated.date == '2020-09-12'].groupby('date').sum()

# # %%

# state_data = pd.merge(state_unallocated, state_county_count, on='state', how='left')

# state_data['county_alloc'] = state_data['weekly_cases'] / state_data['counties']

# state_data = state_data[['date','state', 'county_alloc']]

# state_data[state_data.date == '2020-09-12']


# %%

confirmed_cases = result

# %%

# write the cases to a file
import numpy as np
for id, df_i in enumerate(np.array_split(confirmed_cases, 3)):
    df_i.to_csv('confirmed_daily_cases{id}.csv'.format(id=id), index=False)
# %%
