# Northampton County Web Scraper
## (scrapes public tax data hosted on the county website) 

### How To:
1)	Open a command prompt.
2)	Navigate to the working directory (the location of the python script).
3)	Execute the following command. Use either the 'man' flag to manual select the date range and municipality of the scrape, or use the 'auto' flag to auto-scrape 10 years of data from all 37 Northampton municipalities:

```python scrape.py [man\auto]```

4)	Complete prompts from the script if using 'man' flag.
5)	Output .csv files are generated to the current working directory. They are named by municipality. 

### Import .CSV to Google Sheets for Analysis:
1)	Open a new google sheet.
2)	Select "File"->"Import"->"Upload"->"Select a file from your device"->"output.csv".
3)	Under "Selector Type: select "Custom:" and enter "|". Then select "Import Data".
4)	Select all of row "1" then select "Data"->"Create Filter" to add column filters.

### Import .CSV to R for Analysis:
todo
