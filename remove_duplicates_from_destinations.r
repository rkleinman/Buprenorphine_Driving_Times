library(stringr)
library(dplyr)

f = "C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\geocoded_output.csv"


data = read.csv(f)


data_subset = distinct(data,LONGITUDE,LATITUDE, .keep_all = TRUE)
write.csv(data_subset,"C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\destinations_wo_duplicates.csv")







