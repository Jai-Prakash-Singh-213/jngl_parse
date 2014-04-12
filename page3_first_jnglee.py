import ast
from urlparse import urlparse
from bs4 import BeautifulSoup
import req_proxy
import re
import sys
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s', )




def main4(line, filename):
    f = open(filename, "a+")

    sl = line[-2]
    st = line[-1]
    
    page = req_proxy.main(sl)

    soup = BeautifulSoup(page)

    tag_depatrmen = soup.find("h2", text=re.compile("Department"))
    tag_ul = tag_depatrmen.find_next("ul")

    tag_strong = tag_ul.find("strong", text = re.compile(st))

    parent_li = tag_strong.find_parent("li")

    tag_narrow = None

    try:
        parent_li = parent_li.find_next_sibling()
        tag_narrow = parent_li.find("span", attrs={"class":"narrowValue"})

    except:
        print >>f, line  + line[-2:]
        print line  + line[-2:]

    loop = True

    while loop is True:
        if tag_narrow is not None:
            tag_narrow = tag_narrow.parent
            sctlink = "%s%s" %("http://www.junglee.com", tag_narrow.get("href"))
            scttitle = tag_narrow.get_text().encode("ascii", "ignore").strip()
            print >>f, line +  [sctlink, scttitle]
            print line +  [sctlink, scttitle]
           
            tag_narrow_li = tag_narrow.find_next("a")
            tag_narrow = tag_narrow_li.find("span", attrs={"class":"narrowValue"})

        else:
            loop = False

    f.close()




def main3(line, filename):
    try:
        main4(line, filename)

    except:
        f = open("page3_first_jnglee_error.txt", "a+")
        print >>f, line
        f.close()

    time.sleep(1)




def main2(forsubcat_ml_mt_cl_ct_sl_st):
    f = open("to_extract_jnglee.txt")
    directory = f.read().strip()
    f.close()
    
    filename = "%s/forsubcat_ml_mt_cl_ct_sl_st_ssl_sst.txt" %(directory)

    for line in forsubcat_ml_mt_cl_ct_sl_st:
       print line
       t = threading.Thread(target=main3, args=(line, filename))
       #t.setDaemon(True)
       t.start()
   
    main_thread = threading.currentThread()
    
    for t in threading.enumerate():
        if t is main_thread:
	    continue
        logging.debug('joining %s', t.getName())
	t.join(2)
    

    

def main():
    f = open("to_extract_jnglee.txt")
    directory = f.read().strip()
    f.close()

    filename1 = "%s/ml_mt_ct_cl.txt" %(directory)
    filename2 = "%s/ml_mt_cl_ct_sl_st.txt" %(directory)

    f = open(filename1)
    line1 = f.read().strip()
    f.close()

    line_lsit1 = ast.literal_eval(line1)

    f = open(filename2)
    line2 = f.read().strip()
    f.close()
         
    line_lsit2 = ast.literal_eval(line2)

    forsubcat_ml_mt_cl_ct_sl_st = []

    for ln in line_lsit1:
        link = ln[-2]
	parsed = urlparse(link)

	if filter(None, parsed.path.split("/"))[0] == 's': 
            forsubcat_ml_mt_cl_ct_sl_st.append(ln)
    for ln in  line_lsit2:
        link = ln[-2]
        parsed = urlparse(link)

        if filter(None, parsed.path.split("/"))[0] == 's':
            forsubcat_ml_mt_cl_ct_sl_st.append(ln)

    filename3 = "%s/forsubcat_ml_mt_cl_ct_sl_st.txt" %(directory)

    f = open(filename3, "w+")
    print >>f, forsubcat_ml_mt_cl_ct_sl_st
    f.close()

    return forsubcat_ml_mt_cl_ct_sl_st




def supermain():
    forsubcat_ml_mt_cl_ct_sl_st = main()
    
    main2(forsubcat_ml_mt_cl_ct_sl_st)
        



if __name__=="__main__":
    supermain()
