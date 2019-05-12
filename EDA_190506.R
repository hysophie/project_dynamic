library(dplyr)
library(tidyr)
library(readr)
library(ggplot2)
library(magrittr)

########################################################################
###Custom Data###
custom <- read_csv('C:\\DynamicData\\Custom.csv')
nrow(custom) #671679 observations

any(is.na(custom))#No NA Values

attach(custom)
length(which(CLNT_GENDER=='M')) #101063 observations for male
length(which(CLNT_GENDER=='F')) #570616 observations for female

summary(CLNT_AGE)
CLNT_AGE.Factor <- factor(CLNT_AGE)
plot(CLNT_AGE.Factor)

custom %>%
  group_by(CLNT_AGE) %>%
  summarise(obs = n())

detach(custom)
#일단은 10대 고민, 70, 80대는 무시해도 된다고 생각. (%)
##########################################################################
###Master Data###
master<- read_csv('C:\\DynamicData\\Master.csv')

head(master)

master_class2 <- master %>%
  group_by(CLAC2_NM) %>%
  select(-CLAC3_NM)

#master_class2_stats : 중분류로 다 정리, 개수 순으로. 
master_class2_stats <- master_class2 %>%
  summarise(obs=n()) %>%
  arrange(desc(obs))

as.data.frame(master_class2_stats)
#개수를 어떻게 끊을 것인가? 

########################################################################
###Product Data###
product <- read_csv('C:\\DynamicData\\Product.csv')

nrow(product) #5024906
nrow(unique(product[,1])) #922737
#같은 사람이지만 다른 기기를 쓰는 사람을 알아낼 수는 없다고 생각.

product_summarise <- product %>%
  group_by(CLNT_ID) %>%
  summarise(num = n()) %>%
  arrange(desc(num))
#3154, 2194, 1827 번 정도 씩 등장하는 이상한 행동 양태를 갖고 있는 사람들?
#이런 소비자들에 대한 논의가 필요하다고 생각.
#이 사람의 행동 양태를 어떻게 생각해볼 수 있을까?

product_summarise
tail(product_summarise)
head(as.data.frame(product_summarise), 20)

product_rank1 <- product[product$CLNT_ID == 4736937,]
product_rank1

ggplot(data=product_rank1, mapping=aes(x=HITS_SEQ, y=PD_BUY_CT))+
  geom_jitter() #Could not find any tendency between two variables

#Uploaded product_rank1 data on github

product_summarise2 <- product %>%
  group_by(CLNT_ID) %>%
  summarise(SESSID = n_distinct(SESS_ID))
product_summarise2 %>%
  arrange(desc(SESSID))
#역시 100번이 넘는 SESSID 발급자 많음.



