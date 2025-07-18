import json
from os.path import join
def gen_hit_level():
    map_data={}
    for i in range(-2,96):
        map_data[str(i%8*75)+"."+str(i//8)]={"type":str(i),"x":i%8,"y":i//8}

    with open(join("./assets/",input("file name:")),mode="w") as f:
        data={"map":map_data,"other":{"cx":0,"cy":0}}
        json.dump(data, f, ensure_ascii=False, indent=4)
def upgrade_level_data(level_data,level_version,pp) -> dict:
    thing = level_data
    # print(thing)
    if level_version == 1.0 or level_version == 1.1:
        print("unrecoverable")
        return {"type":-1}
    elif level_version == 1.2:
        # print("but its")
        # print(thing)
        for block in thing:
            # print(block)
            thing[block]["chunk-x"] = round((thing[block]["x"]-pp["cx"])//10-1)
            thing[block]["chunk-y"] = round((thing[block]["y"]-pp["cy"])//10-1)
    # print(thing,"link")
    return thing
