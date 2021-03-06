import numpy as np
import requests
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from check_times import check_if_and_times
from class_shop import Shops


#----Read a .txt file that contains the product urls 
url = []
n_products = 0
with open('product_urls.txt', 'r+', newline='') as products:
    for product in products:
        url.append(product.strip())
        n_products = n_products + 1

print('Number of products:', n_products)
#------------------------------------------------------

#------Find the shops that provide all products--------
tot_counter = np.zeros(n_products, dtype=int)
urls = []
parts = [None]*4

for i in range(n_products):    
    driver = webdriver.Chrome() 
    driver.get(url[i])
    results = driver.find_elements(By.XPATH, "//*[@class='card js-product-card' or @class='card js-product-card has-pro-badge']")
    
    #results = soup('li', class_ = ['card js-product-card', 'card js-product-card has-pro-badge'])
    shop_count = 0

    #find the common shops by comparing shop ids
    for result in results:
        shop_ids = result.get_attribute('id')
        parts = shop_ids.split('-')
        shop_id = int(parts[1])
        urls.append(shop_id)
        shop_count = shop_count + 1

    driver.close()     
    #Keep the total number of shops that provide each product
    tot_counter[i] = shop_count

#The ids of common shops are kept in sim_indices[]
sim_indices = []
sim_tot = np.zeros(n_products-1, dtype=int) #tracks the number of shops per 2,3,4... products
for i in range(2, n_products+1):
    pos_count = 0
    for j in range(len(urls)):
        #count only the unique indices
        if urls.count(urls[j]) == i and sim_indices.count(urls[j]) < 1:
            sim_indices.append(urls[j])
            pos_count = pos_count + 1
    
    sim_tot[i-2] = pos_count
    if len(sim_indices) >= 1:
        print(i, 'of the products can be found in', pos_count, 'shops')


#--------Web scrap each link to retrieve the rest shop attributes-----
if len(sim_indices) >= 1:
    #We are looking for the shop that has the most products that can be found at the bottom of the list
    last_nonzero = np.max(np.nonzero(sim_tot))
    optimal_list = sim_indices[-sim_tot[last_nonzero]:]
    #----------------------------------------------------------

    shop_strings = []
    for j in range(len(optimal_list)):
        shop_strings.append('shop-'+str(optimal_list[j]))

    #write csv file    
    f = open('Skroutz_shops.csv', 'w', encoding='UTF8', newline='')
    header = ['Product', 'Shop name', 'Shop url', 'Initial price', 'Skroutz transportation fees', 'Skroutz transaction fees', 'Shop transportation fees',
             'Shop transaction fees', 'Rating', 'Total reviews', 'Availability', 'Location']
    wr = csv.writer(f)
    wr.writerow(header)

    
    for i in range(n_products):
        try: #in case the product is available in the shop            
            p = Shops(url[i], shop_strings)    
            product = p._product_name()
            price = p._prices()
            if i == 0: #the objects are identical to all products so they are created once
                shop_url = p._shop_url()
                name = p._name()
                rating, tot_rev = p._rating()
                avail = p._availability()
                loc = p._location()
            #----------------------------------------------------------------

            #------------------Print the results in the csv file--------------------
            for j in range(len(shop_strings)):
                if j == 0:
                    wr.writerow([product, name[j], shop_url[j], price[j,0], price[j,1], price[j,2], price[j,3],
                    price[j,4], rating[j], tot_rev[j], avail[j], loc[j]])
                else:
                    wr.writerow(['>>', name[j], shop_url[j], price[j,0], price[j,1], price[j,2], price[j,3],
                    price[j,4], rating[j], tot_rev[j], avail[j], loc[j]])

            wr.writerows('-')        
            #---------------------------------------------------------------------- 
        except:
            continue       
else:
    print('No common shops were found in the provided urls.')
#---------------------------------------------------------------------

