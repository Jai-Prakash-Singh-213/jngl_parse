import req_proxy
from bs4 import BeautifulSoup
from lxml import html
import re
import multiprocessing
import logging
import time 
import os 
import threading
import re 
from urlparse import urlparse
import sys
import ast

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s',)

num_fetch_threads = 20
enclosure_queue = multiprocessing.JoinableQueue()




def mystrip(x):
    return str(x.encode("ascii", "ignore")).replace("\n", " ").replace("\r", " ").replace("\t", " ").replace(",", " ").strip()




def page_for_seller(filename, prodetail):
    f = open(filename, "a+")

    pro_link = prodetail[9]
    
    start = pro_link.find("dp/")
    end = pro_link.find("/", start+3)
    sku = str(pro_link[start+3 : end])

    prodetail.insert(0, sku)

    page2 = req_proxy.main(pro_link)

    soup = BeautifulSoup(page2)

    brand = "undifined"
    
    brand1 = soup.find("div", attrs={"class":"byLine"})
    brand2 = soup.find("td", text=re.compile("Brand"))

    if brand1 is not None:
        brand = str(brand1.a.get_text())
    elif brand2 is not None:
        brand = str(brand2.find_next_sibling("td").get_text()).strip()        
    else:
        pass

    whole_price = soup.find("span", attrs={"class":"whole-price"})
    whole_price = str(whole_price.get_text())

    div_seller = soup.find("table", attrs={"class":"outdent"})

    seller_info = []

    if div_seller is not None:
        seller_info = div_seller.find_all("tbody", attrs={"class":"offer-has-map offer-hidden-map"})

    else:
        sellerinfo = soup.find("div", attrs={"class":"sellerInfo"})
        sellerlink = str(sellerinfo.a.get("href"))
        sellername = filter(None, sellerlink.split("/"))[0]
        sellerlink = "%s%s" %("http://www.junglee.com", sellerlink)
        contact_phone = "not defined"
        offerPrice = whole_price
        shippingPrice = soup.find("div", attrs={"class":"shippingPrice"})
        shippingPrice = str(shippingPrice.get_text())
        seller_site = soup.find("a", attrs={"class":"visitbutton button larger-button"})
        seller_site = "%s%s" %("http://www.junglee.com", str(seller_site.get("href")))
        procomp = [brand, whole_price, sellername, sellerlink, contact_phone, offerPrice, shippingPrice, seller_site]
        procomp = map(mystrip, procomp)
        print >>f, ",".join(prodetail + procomp)
        print  prodetail + procomp

    for dlr in seller_info:
        sellerlink = dlr.find("a", attrs={"class":"sellerLink"})
        sellerlink = str(sellerlink.get("href"))
	sellername = filter(None, sellerlink.split("/"))[0]
	sellerlink = "%s%s" %("http://www.junglee.com", sellerlink)
	contact_phone2 = dlr.find("li", attrs={"class":"contact-phone"})
        contact_phone = "None"

        try:
	    contact_phone = str(contact_phone2.get_text()).strip()
        except:
            pass

	offerPrice = dlr.find("span", attrs={"class":"offer-price"})
	offerPrice = str(offerPrice.get_text())
        shippingPrice = dlr.find("span", attrs={"class":"shippingPrice"})
        shippingPrice = str(shippingPrice.get_text())
        seller_site = dlr.find("a", attrs={"class":"visitbutton button larger-button"})
	seller_site = "%s%s" %("http://www.junglee.com", str(seller_site.get("href")))
	procomp = [brand, whole_price, sellername, sellerlink, contact_phone, offerPrice, shippingPrice, seller_site]
        procomp = map(mystrip, procomp)
        print >>f, ",".join(prodetail + procomp)
        print  prodetail + procomp

    f.close()

        

      
def page_for_seller_main(filename, prodetail):
    try:
        page_for_seller(filename, prodetail)
    
    except:
        f = open("page4_second_error_jnglee.txt", "a+")
        print >>f, prodetail[10]
        f.close()


 

def main_ct_pro(line, directory, nlink = None):
    ml = line[0]
    mt = line[1]
    cl = line[2]
    ct = line[3]

    try:
        if len(line) == 8:
            sl = line[4]
            st = line[5] 
            ssl  = line[6]
            sst = line[7]
            dirnow = "%s/%s/%s/%s/%s" %(directory, mt, ct, st, sst)

        else:
            sl = cl
            st = ct
            ssl  = line[4]
            sst = line[5]
            dirnow = "%s/%s/%s/%s" %(directory, mt, ct, sst)

        os.makedirs(dirnow)

    except:
        pass 
     
    filename =  "%s/%s.csv" %(dirnow, sst)

    if nlink is None:
        page = req_proxy.main(sl)

    else:
        page = req_proxy.main(nlink)

    soup = BeautifulSoup(page)
    
    tag_pro_result = soup.find_all("div", attrs={"id":re.compile("result")})
    
    threads = []
    for pro in  tag_pro_result:
        try:
            pro_img = pro.find("img").get("src") 
	    pro_link_title = pro.find("a", attrs={"class":"title"})
	    pro_link = pro_link_title.get("href")
	    pro_title = pro_link_title.get_text()
	    pro_price = pro.find("span", attrs={"class":"price"}).get_text()
	    pro_seller = pro.find("div", attrs={"class":"offerCount"}).get_text()

	    prodetail = [ml, mt, cl, ct, sl, st, ssl, sst,  pro_img, pro_link, pro_title, pro_price, pro_seller]

	    prodetail = map(mystrip, prodetail)

            t = threading.Thread(target=page_for_seller_main, args=(filename, prodetail,))
	    threads.append(t)
	    t.start()

        except:
            pass

    main_thread = threading.currentThread()

    for t in threading.enumerate():
        if t is main_thread:
            continue
        logging.debug('joining %s', t.getName())
        t.join()

    main_ct_pro.counter  += len(tag_pro_result)

    if main_ct_pro.counter > 200:
        return True
    
    nextpage = soup.find("a", attrs={"id":"pagnNextLink"})
 
    if nextpage is not None:
        nextlink = "%s%s" %("http://www.junglee.com", str(nextpage.get("href")))
	main_ct_pro(line, directory, nlink = nextlink)
        



def part_threading2(i, q):
    for  line, directory in iter(q.get, None):
        try:
            line = ast.literal_eval(line)
            main_ct_pro.counter = 0
            main_ct_pro(line, directory)

        except:
            f2 = open("page4_first_jnglee_error.txt", "a+")
            print >>f2, line
            f2.close()

        time.sleep(2)
        q.task_done()

    q.task_done()




def mainthreading():
    f = open("to_extract_jnglee.txt")
    directory = f.read().strip()
    f.close()

    filename ="%s/forsubcat_ml_mt_cl_ct_sl_st_ssl_sst.txt" %(directory)

    f = open(filename)

    procs = []

    for i in range(num_fetch_threads):
        procs.append(multiprocessing.Process(target=part_threading2, args=(i, enclosure_queue,)))
        procs[-1].start()

    for  line  in f:
        enclosure_queue.put((line, directory))

    print '*** Main thread waiting'
    enclosure_queue.join()
    print '*** Done'

    for p in procs:
        enclosure_queue.put(None)

    enclosure_queue.join()

    for p in procs:
        p.join(2)

    print "Finished everything...."
    print "closing file...."

    f.close()


    

def supermain():
    mainthreading()




if __name__=="__main__":
    supermain()
