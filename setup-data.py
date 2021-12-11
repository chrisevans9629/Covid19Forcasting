# %%
import pandas as pd

# %% [markdown]
# # Step 1
# Read the actual cases and convert the data from wide format to row format

# %%

try:
    files = []
    for i in range(3):
        files.append('confirmed_daily_cases{id}.csv'.format(id=i))
    data = pd.concat(map(pd.read_csv, files), ignore_index=True)
    print('found files for actual daily cases')
    print(data.head(4))
    confirmed_cases = data
except FileNotFoundError:
    import create_act_cases
    confirmed_cases = create_act_cases.confirmed_cases


# %% [markdown]
# ## Step 1.1
# Validate the data  

# %%
confirmed_cases[confirmed_cases.date == '2020-09-12'].groupby('date').sum()

# %%
confirmed_cases

# %%
confirmed_cases['act_cases'] = confirmed_cases['weekly_cases']

confirmed_cases = confirmed_cases.drop(columns=['weekly_cases', 'date_last_week_last_week', 'county_last_week','date_last_week.1', 'act_cases_last_week', 'date_last_week'])

confirmed_cases

# %% [markdown]
# # Step 2
# Read the forcasting data from the multiple files

# %%
item = []
for i in range(6):
    item.append('fcast_data' + str(i+1) + '.csv')    

print(item)

data = pd.concat(map(pd.read_csv, item), ignore_index=True)

# %%
#data = data[data.target == "1 wk ahead inc case"]
#data = data[data.location_name != data.State]
data['date'] = pd.to_datetime(data['target_end_date'])

data = data.rename(columns={'point': "for_cases"})

data = data[['model','date','fips','for_cases','target']]

forcasted_cases = data

forcasted_cases.head(10)


# %% [markdown]
# ## Step 2.1
# Read the population data

# %%
pop_data = pd.read_csv('covid_county_population_usafacts.csv')

pop_data = pop_data[['countyFIPS','population']]

pop_data = pop_data.rename(columns={'countyFIPS': "fips"})

pop_data.head(10)

# %% [markdown]
# # Step 3
# Merge the two datasets together based on predication target date and the county

# %%
forcasted_cases['fips'] = forcasted_cases['fips'].astype(str)
forcasted_cases['date'] = forcasted_cases['date'].astype(str)

confirmed_cases['fips'] = confirmed_cases['fips'].astype(str)
confirmed_cases['date'] = confirmed_cases['date'].astype(str)

all_cases = pd.merge(forcasted_cases, confirmed_cases, on=['date','fips'], how='inner')

all_cases.head(10)

# %%
all_cases[all_cases.date == '2020-09-12'].groupby(['date','fips']).mean().groupby('date').sum()

# %% [markdown]
# # Step 3.1 
# Merge population data with all cases

# %%
pop_data['fips'] = pop_data['fips'].astype(str)

all_cases = pd.merge(all_cases, pop_data, on=['fips'], how='inner')
# add error calculations here 
all_cases.head(10)

# %% [markdown]
# Write the dataset to a file

# %%
all_cases.to_csv('all_cases.csv')

# %% [markdown]
# # Data Validation Test

# %%
all_cases[(all_cases.state == "MO") & (all_cases.county == "Jackson County ") & (all_cases.model == "Columbia") & (all_cases.target == "1 wk ahead inc case")].sort_values(by='date')

# %%
all_cases[(all_cases.state == "AK") & (all_cases.county == "Aleutians East Borough ") & (all_cases.model == "Columbia") & (all_cases.target == "1 wk ahead inc case")].sort_values(by='date')


# %%
all_cases[(all_cases.for_cases < 0)]


