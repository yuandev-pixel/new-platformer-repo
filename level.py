import json
from os.path import join
map_data={}
for i in range(-2,96):
    map_data[str(i%8*75)+"."+str(i//8)]={"type":str(i),"x":i%8,"y":i//8}

with open(join("./assets/",input("file name:")),mode="w") as f:
    data={"map":map_data,"other":{"cx":0,"cy":0}}
    json.dump(data, f, ensure_ascii=False, indent=4)
