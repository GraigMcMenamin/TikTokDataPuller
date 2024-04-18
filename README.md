# TikTokDataPuller
This program automates the process of pulling data using TikTok’s research API, by generating and running requests to the API, as well as organizing response data into csv files. This program was built for those that have been granted access to TikTok's research API. You will need to enter your client key and secret to use this program.
- All information about parameters and response data can be found on TikTok's API documentation here: https://developers.tiktok.com/doc/about-research-api/
- Response csv files will be named by default with the format "yyyy-mm-dd hh-mm-ss.csv" using the date and time.
- To receive the next page of data for the same query, enter the count number that you've already received as the cursor. For example if you use max count 100, to get the first three pages, you would use cursors 0, 100, 200.
