import json
from os.path import join
map_data={}
for i in range(-2,96):
    map_data["0."+str(i)]={"type":i,"x":0,"y":i}

with open(join("./assets/",input("file name:")),mode="w") as f:
    data={"map":map_data,"other":{"cx":0,"cy":0}}
    json.dump(data, f, ensure_ascii=False, indent=4)
