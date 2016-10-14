library(rvest)
library(magrittr)
library(xml2)
library(stringr)
#library(doParallel)

#找出總共有幾頁
page_limit<- function(){
  page_init <- paste0(domain_base,2,'&psl=N_B') %>% read_html()
  page_total <- page_init %>% html_nodes('.next_page #loadDone_3') %>% html_text() %>% gsub("[^，0-9]+", "",.) %>% strsplit('，')
  page_total <- as.numeric(page_total[[1]][2])
  return(page_total)
}

#每頁的工作機會url
urls <- function(page){
  domain <- 'http://www.104.com.tw'
  all_url <- list()
  for (i in 1:page){
    page_104 <- paste0(domain_base,i,'&psl=N_B') %>% read_html()
    #in_page <- rep(i,length(job_url))
    job_url_node <- page_104 %>% html_nodes('.line_bottom[itemtype="http://schema.org/JobPosting"] .job_name a') 
    for (each in job_url_node){
      job_url <- each %>% html_attr('href') %>% paste0(domain,.) %>% str_trim()
      #等同於str_trim(paste0(domain,html_attr(each,'href')))
      all_url <- append(all_url,job_url)
    }
    print(i)}
  return(all_url)}

#每個url的資訊爬取
get_element <- function(url){
  
  all_element <- data.frame()
  
  tryCatch({
    url_read <- url %>% read_html()
    job_url <- url
    job_name <- url_read %>% html_nodes('.main .center h1') %>% html_text() %>% strsplit('\r')
    job_name <- job_name[[1]][2] %>% str_trim()
    
    company <- url_read %>% html_nodes('.company a.cn') %>% html_text()
    
    competitors <- url_read %>% html_nodes('.function .sub img[src]') %>% html_attr('alt') %>% strsplit(' ')
    competitors <- competitors[[1]][2]
    
    job_content <- url_read %>% html_nodes('.main .info .content p:nth-child(1)') %>% html_text()
    job_content <- job_content[1] %>% gsub("\r", "",.) %>% gsub("\t", "",.) %>% gsub("\n", "",.) %>% gsub(" ", "",.)
    
    job_category <- url_read %>% html_nodes('.main .info .content dd.cate') %>% html_text() %>% strsplit('\t')
    job_category <- job_category[[1]][2] %>% str_trim()
    
    job_require_nod <- url_read %>% html_nodes('.main > section:nth-child(2) .content dd') %>% html_text()
    experience <- job_require_nod[2]
    degree <- job_require_nod[3]
    department <- job_require_nod[4] 
    tools <- job_require_nod[6]
    skills <- job_require_nod[7]
    others <- job_require_nod[8] %>% gsub("\r", "",.) %>% gsub("\t", "",.) %>% gsub("\n", "",.) %>% gsub(" ", "",.)
    
    update_time <- url_read %>% html_nodes('time.update') %>% html_text() %>% gsub("更新日期：", "",.) %>% str_trim()
    all_element <- data.frame(job_url,update_time,job_name,company,competitors,job_content,job_category,experience,degree,department,tools,skills,others)
  },error = function(err) {
    print(url)})
  
  return(all_element)
}

# ======= mission start =========
starttime <- Sys.time()

domain_base <- 'http://www.104.com.tw/jobbank/joblist/joblist.cfm?jobsource=n104bank1&ro=0&keyword=%E8%B3%87%E6%96%99%E7%A7%91%E5%AD%B8&area=6001001000%2C6001002000%2C6001006000&order=1&asc=0&page='

page <- page_limit()
joburls <- urls(page)

scraped_data <- data.frame()
n <- 0
for (each in joburls){
  data <- get_element(each)
  scraped_data <- rbind(scraped_data,data)
  n <- n+1
  print(n)
}

saveRDS(scraped_data, "scraped_data.rds")
new <- readRDS("scraped_data.rds")

runtime <- Sys.time() - starttime
runtime

# ======== 以後研究 =========
#core <- detectCores()-1
#(cl <- (detectCores() - 1) %>%  makeCluster) %>% registerDoParallel

#testframe <-data.frame()

#ws <- foreach(i = 1:length(joburls), .combine = 'rbind', .packages = c('rvest', 'magrittr', 'xml2','stringr')) %dopar% {

#  text1 <- unlist(joburls[i], function(url) get_element(url))
#  testframe <- rbind(testframe,text1)
  
#}
