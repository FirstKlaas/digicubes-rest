from time import gmtime, strftime

t = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
print(t)