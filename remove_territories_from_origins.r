library(stringr)

f = "C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\origins.csv"
data = read.csv(f)
data_subset = subset(data, data$STATEFP != "72")

write.csv(data_subset,"C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\origins_wo_pr.csv")

