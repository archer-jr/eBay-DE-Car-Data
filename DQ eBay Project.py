
# coding: utf-8

# This is an eBay Germany project, looking at used car sales data.
# The aim is to clean and analyse the provided data (50,000 rows).

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


autos = pd.read_csv("autos.csv", encoding="Latin-1")


# In[3]:


autos[:5]


# In[4]:


autos.info()
autos.head()


# From looking at the above data, there is some missing detail, including a few thousand models (could they be known as a make only, or is it missing?). Some other pieces of data are also missing.
# The data itself has an index value, date/time, a few different types of vehicle, 2 options for gearbox that I see. I also notice that powerPS is set as 0 for row 5, this may be a mistake, or maybe the car doesn't run? It depends on what it is actually defined by.

# In[5]:


autos.columns


# In[6]:


new_columns = ['date_crawled', 'name', 'seller', 'offer_type', 'price', 'abtest',
       'vehicle_type', 'registration_year', 'gearbox', 'power_ps', 'model',
       'odometer', 'registration_month', 'fuel_type', 'brand',
       'unrepaired_damage', 'ad_created', 'nr_of_pictures', 'postal_code',
       'last_seen']
autos.columns = new_columns


# In[7]:


autos.columns


# In[8]:


autos.head()


# I have converted the headers, removing the camelcase and changing to snakecase. I first listed the columns, copied them into a new list. I then edited the new list, and assigned the columns as the new list.

# In[9]:


autos.describe(include="all")


# Columns that can be dropped due to being mostly one value are "seller" and "offer_type". "price" and "odometer" are both numerical values in a string column, so need to be changed.

# In[10]:


autos["price"] = autos["price"].str.replace("$","")
autos["price"] = autos["price"].str.replace(",","")
autos["price"] = autos["price"].astype(int)


# In[11]:


autos["odometer"] = autos["odometer"].str.replace("km","")
autos["odometer"] = autos["odometer"].str.replace(",","")
autos["odometer"] = autos["odometer"].astype(int)
autos = autos.rename(index=str, columns={"odometer": "odometer_km"})


# In[12]:


autos.columns


# In[13]:


autos["odometer_km"].unique().shape
autos["odometer_km"].describe()


# In[14]:


autos["odometer_km"].sort_index(ascending=True)


# In[15]:


pd.options.display.float_format = '{:20,.2f}'.format
autos["price"].head().value_counts


# In[16]:


autos = autos[autos["price"].between(100,500000)]


# In[17]:


autos["price"].describe()


# There were no outliers for the odometer values, the maximum of 150,000 seems well within range (my first car was close to that!), and a minimum of 5000 is okay, even 10% of that would have been fine, especially for a new car.
# 
# Price wise, The maximum price seemed too high and was skewing the statistics. I made the maximum price 500,000, and this returned data with a maximum of 350,000. I don't see why this wouldn't be feasible, but it may be worth looking into this value to ensure it is normal. I could potentially lower the threshold otherwise, possibly to 300,000.

# In[18]:


autos["registration_month"].describe()


# In[19]:


autos["date_crawled"] = autos["date_crawled"].str.replace("-","")
autos["date_crawled"] = autos["date_crawled"].str[:8]
print(autos["date_crawled"].value_counts(normalize=True, dropna=False).sort_index())


# From the above values, we can notice a pretty even distribution between dates in this series. The majority of dates were between 3-4%, and none reached 5%. This isn't overly surprisingly given this is just checking the crawler dates!

# In[20]:


autos["ad_created"] = autos["ad_created"].str.replace("-","")
autos["ad_created"] = autos["ad_created"].str[:8]
print(autos["ad_created"].value_counts(normalize=True, dropna=False).sort_index())


# Looking at the dates the ads were created, we can see there is some very sparse data prior to January 2016, and many dates before this time had no adverts created. The later dates appear to have a much larger proportion of the data, and many days have between 3-4% of listings, and each day appears to have had listings.

# In[21]:


autos["last_seen"] = autos["last_seen"].str.replace("-","")
autos["last_seen"] = autos["last_seen"].str[:8]
print(autos["last_seen"].value_counts(normalize=True, dropna=False).sort_index())


# The above details when the crawler last saw the ad online. This may be due to an automatic deletion by eBay? Around half of the adverts were last seen in the final 3 days of the stufy, leading me to believe they were likely still on eBay at the time the crawler ended. The rest of the days usually have between 1-3% of the values, the first few having far less. This also makes sense, because it is likely the crawler picked up a large mix, and only a small proportion will end early. I am struggling to account for why this increases to 3-4% for the majority of the days. Will be worth double checking how the data was collected!

# In[22]:


autos["registration_year"].describe()


# I will have to double check how to tell Pandas to return values without the commas. The above data should that the minimum is 1000 - this is obviously impossible, so should be dropped. The interquartile ranges all look realistic, and the mean being approximately 2004. The maximum of 9999 is also impossible, so these outliers should be removed.
# For this exercise, I will be happy to accept years between 1900 - 2016. 1900 was chosen rather arbitarily, and I would like to see the values for around this time. A cut-off of 2016 makes sense, because the data was collected in 2016 and any later values are not possible.

# In[23]:


outlier_years = []
outlier_years = autos[~autos["registration_year"].between(1900,2016)]
outlier_years


# In[24]:


lier_years = []
lier_years = autos[autos["registration_year"].between(1900,2016)]
lier_years


# In[25]:


years_acceptable = autos[autos["registration_year"].between(1900,2016)]


# In[26]:


years_acceptable["registration_year"].value_counts(normalize=True).sort_index()


# Firstly, I wasn't too sure on whether to remove the values from the original data, so I created a side list of acceptable years. From the data, there were very few cars in the earlier years. The earliest car reg date was 1910, and there wasn't another until 17 years later. This could be an outlier. The later years, from 1990 onwards each contain at least 1% of the car listings. The most common year is 2000 with around 7% of cars produced then. Between 2001-2010, each year had approximately 5-7% produced in each.

# In[27]:


print(autos["brand"].unique())


# In[28]:


brands = autos["brand"].value_counts(normalize=True)
brands


# I will now aggregate the data based on the car brand. The above has the percentage for each brand in the eBay listings (the normalize=True shows the percentage, it is False by default which returns the raw number of listings).
# I will select all brands with at least 5% of the listings to ensure sufficient data is available. This will be: Volkswagen (21%), BMW (11%), Opel (11%), Mercedes-Benz (10%), Audi (9%), Ford (7%) and Renault (5%). The next highest brand is Peugeot with 3%, well under our cut-off.

# In[29]:


top_brands = autos["brand"].value_counts().head(6)
top_brands    


# In[30]:


means_dict = {}
brand_names = top_brands.index

for vals in brand_names:
    average = autos.loc[autos["brand"] == vals, "price"].mean() # makes sense reading it!
    means_dict[vals] = round(average, 2)
means_dict


# From the above data (which I required a little help with), I can see that Audi is the most expensive brand, with a mean of over 9250. The least expensive is Opel at under 3000. Volkswagen is a mid-range car, with Mercedes and BMW both being on the expensive end, and Ford at the budget end.

# Next, I want to look at the average milage of the above cars, and see if this correlates with the mean price.
# It's better to use a separate dataframe for this, as it makes it easier to sort and compare large amounts of data.
# Need to use a pandas series constructor and dataframe constructor.
# For a pandas series from a dictionary, the keys become the index, can also set the column name.
# i.e. df = pd.DataFrame(bmp_series, columns=['mean_mileage']).

# In[38]:


milage_means = {}
for vals in brand_names:
    average = autos.loc[autos["brand"] == vals, "odometer_km"].mean()
    milage_means[vals] = round(average, 2)
milage_means


# In[48]:


brands_pricemeans = pd.Series(means_dict)
brands_milagemeans = pd.Series(milage_means)


# In[49]:


brands_dataframe = pd.DataFrame(brands_pricemeans, columns=["mean_price"])
brands_dataframe["mean_milage"] = brands_milagemeans


# In[51]:


brands_dataframe.describe()


# The above dataframe makes the values clear. The mean milage seems to have little effect on the prices, as the cheapest cars don't seem to have lower milages particularly, and the means are all very close! In fact, the SD for milage is very low, less than 3000, which is neglible compared to the mean of nearly 130,000!
