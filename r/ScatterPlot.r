# Scatterplot Script for Northampton Sales Data | Created 3/10/19 | Garrett Grube 

# update these vars before running script
DATA_PATH <- "Desktop/Freelance/NorthamptonCountyWebScraper/output.csv" # Location of output.csv file
GRAPH_TITLE <-"Forks Township Residential Sales 2009-2019 (1,000 - 2.5 mil)" # Title of scatter plot

#Import readr library
library(readr)                                                          
 
#Import and format data                                                                       
D1 <- read_delim(DATA_PATH, "|", 
  escape_double = FALSE, col_types = cols(Date = col_date(format = "%m/%d/%Y"), 
  Price = col_number(), dc1 = col_skip(), dc2 = col_skip(),
  dc3 = col_skip()), trim_ws = TRUE)

# Cast data columns Date and Price to x and y for readability
x <- D1$Date						
y <- D1$Price						

# Generate Scatter Plot
plot(x, y, main=GRAPH_TITLE, 
   xlab="Sale Date ", ylab="Sale Price ($)", 
   pch=19, frame = FALSE, col = "blue")	

# Add regression line															
abline(lm(x ~ y, data = D1), col = "red")
