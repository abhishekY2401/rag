import pandas as pd
import requests
from bs4 import BeautifulSoup

final = pd.DataFrame()

for j in range(1,11):

  url = f'https://www.ambitionbox.com/list-of-companies?page={j}'
  headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
  webpage = requests.get(url,headers=headers).text

  soup = BeautifulSoup(webpage,'lxml')

  companies = soup.find_all('div',class_='companyCardWrapper')
  name = []
  rating = []
  reviewCount = []
  salaries = []
  jobs = []

  for i in companies:
    name.append(i.find('a').text.strip())
    rating.append(i.find('span',class_='companyCardWrapper__companyRatingValue').text.strip())
    reviewCount.append(i.find_all('span',class_='companyCardWrapper__ActionCount')[0].text.strip())
    salaries.append(i.find_all('span',class_='companyCardWrapper__ActionCount')[1].text.strip())
    jobs.append(i.find_all('span',class_='companyCardWrapper__ActionCount')[3].text.strip())
  
    d={'name':name,'rating':rating,'reviewCount':reviewCount,'salaries':salaries,'jobs':jobs}
    df=pd.DataFrame(d)
    
  final = final.append(df,ignore_index=True)