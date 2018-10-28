# Buy2Sell
## Converting collectors to buyers for Covetly, an online marketplace

# Table of content
1. [Problem](README.md#problem)
2. [Approach](README.md#approach)
3. [Technical Architecture](README.md#technical-architecture)
5. [Code Structure](README.md#code-structure)
6. [Contacts](README.md#contacts)

# Problem
Covetly suffers from the high virance of inventory levels across categories. To add inventory for categories
 in shortage, the client expects this project can suggest a list of collectors who can be prompt to sell. 
 However, simply prompting collectors with related inventory is not good enough. Firstly, the converted sellers 
 should be able to sell actively because the platform actually may lose money if the seller only complete one or two
 orders per year due to management cost. Secondly, the seller's inventory composition should match the company's need
 very well. It is not so good if a seller tries to sell things the platform already has high inventory.
 
 
# Approach
This project provide an approach to increase inventory levels by converting collectors to sellers. The model pipeline
comprises of three components. Firstly, the model use classification method to find the similarity between consumption
behaviors of sellers who sold multiple orders in the past. The model is then used to predict the probability of selling
for each collector. The second step provides a percentage by matching inventory composition to categories in shortage. 
At the end, the final score is the multiplication of the probability and percentage. 

# Technical Architecture
The data is from the client's MongoDB and MSSQL databases. A data warehouse is created on AWS RDS which can be updated 
daily. On the data warehouse, about 12 tables are created containing aggregate data for model and webapp. The model and 
webapp are hosted on AWS EC2. 

# Code Structure

    ├── README.md 
    ├── run.sh
    ├── src
    │   └── cache.py
    │   └── connLocalDB.py
    │   └── connMongo.py
    |   └── downloadFromCovetly.py
    │   └── modelTraining.py
    │   └── syncAwsRDS.py
    │ 
    ├── webapp
    │   └── app.py
    │   └── controls.py
    │   └── dashInterface.py
    ├── data
        └── logo.png

# Contact
The webapp is on tianshi-wang.com </br>
Feel free to contact me if you have any question.

Tianshi Wang </br>
tianshi_wang@outlook.com
https://www.linkedin.com/in/tianshi-wang/
