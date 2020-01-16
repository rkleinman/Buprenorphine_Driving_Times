library(stringr)
library(stringi)
library(tidyr)

f="C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\Physician_Locator_2020-01-15T20-50-45.csv"
#f =file.choose()
data = read.csv(f)
data_subset = subset(data, data$State != "Puerto Rico" & data$State != "Virgin Islands"&data$State != "Guam"&data$State != "Northern Mariana Islands")


data_subset$Address_start =  str_locate(data_subset$Address, "\\d")
  

data_subset$Address = str_sub(data_subset$Address, data_subset$Address_start[,1], -1 )




drop = "Address_start"
data_subset = data_subset[ , !(names(data_subset) %in% drop)]


#Ensures that a space is present after Street Endings
#f1 = "C:\\Users\\rkleinma\\Desktop\\filesforbuprenorphineanalysis\\street_suffix.csv"
#data_endings = read.csv(f1)
unit_address_exact = c("Street", "Road", "STREET", "Ste\\.","STE", "St\\.", "ST\\.", "Rd", "ROAD", "RD\\.", "Avenue" ,"Parkway","AVE\\.", "AVENUE", "Ave\\.", "AV", "Drive", "Dr\\.", "DR", "Circle","Crescent","Route", "Rte", "RTE", "Square", "SQ", "Sq\\.", "Ste","Rm")

unit_address = c("apt", "apartment", "suite",  "room", "#", "office", "unit", "building", "bldg", "floor", "flr", "boulevard", "blvd", "highway","expresseway")
#unit_address_exact = c("Ste", "Rm", "Suit")


for (i in 1:length(data_subset$Address)){
  for (x in 1:length(unit_address)){
    index = str_locate(data_subset$Address[i], regex(unit_address[x], ignore_case = TRUE))
    index_1 = index[1,1]
    index_2 = index[1,2]
    if (! is.na(index_1)){
        if ((str_sub(data_subset$Address[i],index_1,index_1)!="")&(str_sub(data_subset$Address[i],index_1,index_1)!=" ")&(str_sub(data_subset$Address[i],index_1-1,index_1-1)!=" ")){
          stri_sub(data_subset$Address[i], index_1, index_1-1) <- " "
        }
      index = str_locate(data_subset$Address[i], regex(unit_address[x], ignore_case = TRUE))
      index_1 = index[1,1]
      index_2 = index[1,2]
        if ((str_sub(data_subset$Address[i],index_2,index_2)!="")&(str_sub(data_subset$Address[i],index_2,index_2)!=" ")&(str_sub(data_subset$Address[i],index_2+1,index_2+1)!=" ")){
          stri_sub(data_subset$Address[i], index_2+1, index_2+0) <- " "
        }
    }
  }
  for (x in 1:length(unit_address_exact)){
    index = str_locate(data_subset$Address[i], unit_address_exact[x])
    index_1 = index[1,1]
    index_2 = index[1,2]
    if (! is.na(index_1)){
      if ((str_sub(data_subset$Address[i],index_1,index_1)!="")&(str_sub(data_subset$Address[i],index_1,index_1)!=" ")&(str_sub(data_subset$Address[i],index_1-1,index_1-1)!=" ")){
        stri_sub(data_subset$Address[i], index_1, index_1-1) <- " "
      }
      index = str_locate(data_subset$Address[i], unit_address_exact[x])
      index_1 = index[1,1]
      index_2 = index[1,2]
      if ((str_sub(data_subset$Address[i],index_2,index_2)!="")&(str_sub(data_subset$Address[i],index_2,index_2)!=" ")&(str_sub(data_subset$Address[i],index_2+1,index_2+1)!=" ")){
        stri_sub(data_subset$Address[i], index_2+1, index_2+0) <- " "
      }
    }
  }
  index_digit = str_locate_all(data_subset$Address[i], "\\d")[[1]]
  index1 = 0
  index2 = 0
  index3 = 0
  z = 0
  repeat{
      z = z + 1
      if (z>nrow(index_digit)){
        break
      }
      index_digit = str_locate_all(data_subset$Address[i], "\\d")[[1]]
      index1 = index_digit[z,1]
      index2 = index1
      repeat{
        if (z<nrow(index_digit)){
          if (index_digit[z+1,1]==(index2+1)){
            index2 = index2 + 1
            z = z +1
          }else{
            break
          }
        }else{
          break
        }
      }
      if (!is.na(index_1)){
      if (index1>1){
        a = str_sub(data_subset$Address[i],index1-1,index1-1)  
        if ((a!="\\d")&(a!="\\.")&(a!="\\-")){
          stri_sub(data_subset$Address[i], index1, index1-1) <- " "
          index1 = index1+1
          index2 = index2+1
        }
      }
        if ((index2)<length(data_subset$Address[i])){
        a = str_sub(data_subset$Address[i],index2+1,index2+1)
        if ((a!="\\d")&(a!="\\.")&(a!="\\-")){
          stri_sub(data_subset$Address[i], index2+1, index2+0) <- " "
        }
        }}else{break}
      }
    }




names(data_subset)[names(data_subset) == 'Last'] = "NAME"
names(data_subset)[names(data_subset) == 'City'] = "CITY"
names(data_subset)[names(data_subset) == 'Address'] = "ADDRESS"
names(data_subset)[names(data_subset) == 'County'] = "COUNTY"
names(data_subset)[names(data_subset) == 'State'] = "STATE"
names(data_subset)[names(data_subset) == 'Postal.Code'] = "ZIP"

#Find digit, if not followed by a digit, dash, comma or period, insert a space




# 
#     index = stri_locate_all_fixed(data_subset$Address, unit_address,   opts_fixed = list(case_insensitive = TRUE))
#     if (nrow(index)>0){
#     for (z in 1:nrow(index)){
#       index_1 = index[z,2]
#       if ((str_sub(data_subset$Address,index_1,index_1)!="")&(str_sub(data_subset$Address,index_1,index_1)!=" ")&(str_sub(data_subset$Address,index_1+1,index_1+1)!=" ")){
#         data_subset$Address = stri_sub(data_subset$Address, index_1+1, index_1) <- " "
#       }
#     }}
#   }  
#     
#   
# }

#data_subset$Address_start =  str_locate_all(data_subset$Address, "\\d")

#check each location of a digit, if not followed by a digit, a dash, comma, or period, insert a space
#check location of south, east, north, west, and ensure followed by a space

#Remove duplicates


write.csv(data_subset,"C:\\Users\\rkleinma\\Desktop\\Buprenorphine_01_2020\\buprenorphine_locations_wo_territories_reformatted_address.csv")


