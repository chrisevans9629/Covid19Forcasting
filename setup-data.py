# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd

# %% [markdown]
# # Step 1
# Read the actual cases and convert the data from wide format to row format

# %%

try:
    files = []
    for i in range(2):
        files.append('confirmed_daily_cases{id}.csv'.format(id=i))
    data = pd.concat(map(pd.read_csv, files), ignore_index=True)
    print('found files for actual daily cases')
    print(data.head(4))
    confirmed_cases = data
except FileNotFoundError:
    print('could not find daily cases files.  regenerating...')
    data = pd.read_csv('covid_confirmed_usafacts.csv')
    # convert column wide to rows
    data = data.melt(id_vars=["countyFIPS","County Name", "State", "StateFIPS"], var_name="date", value_name="value")
    print(data.head(4))

    # select columns
    data = data[['countyFIPS','value','date', 'County Name', 'State']]

    data['date'] = pd.to_datetime(data['date'])

    # rename columns
    data = data.rename(columns={"countyFIPS": "fips", "value": "act_cases", "County Name": "county", "State": "state"})

    print(data.head(10))

    # gets the previous row value
    def getDaily(values):
        daily = []
        length = len(values)
        for i in range(length):
            if i == 0:
                daily.append(values[i])
            else:
                daily.append(values[i]-values[i-1])
        return daily

    # get the counties
    counties = data.groupby('fips')

    dataset = pd.DataFrame()

    # for each county, sort by date and get the daily cases for each county
    for key, county in counties:
        county = county.sort_values(by='date').reset_index()
        act_cases = county['act_cases']
        county['daily_cases'] = getDaily(act_cases)
        dataset = dataset.append(county)

    dataset['act_cases'] = dataset['daily_cases']

    dataset = dataset.drop(['daily_cases','index'], 1)

    confirmed_cases = dataset
    # write the cases to a file
    import numpy as np
    for id, df_i in enumerate(np.array_split(confirmed_cases, 2)):
        df_i.to_csv('confirmed_daily_cases{id}.csv'.format(id=id), index=False)

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


