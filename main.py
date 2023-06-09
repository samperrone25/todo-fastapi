from fastapi import FastAPI, Query, Path # api framework
from typing import Annotated # validation in api
from pydantic import BaseModel # data model
import time # timestamping
import redis # redis
import json

class Item(BaseModel):
    id: int
    title: str
    description: str | None = None
    done: bool = False
    timestamp: float = time.time()

    def toDict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "done": self.done,
            "timestamp": self.timestamp
        }

rDB = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

item1 = Item(id=0, title="bins", description="take them out")
item2 = Item(id=1, title="car")
item3 = Item(id=2, title="room", description="tidy")
items = []
items.append(item1)
items.append(item2)
items.append(item3)

dict1 = item1.toDict()
json1 = json.dumps(dict1)
rDB.set("item1", json1)
print(rDB.type("item1"))
ans = rDB.get("item1")
res = json.loads(ans)
print(res["description"])
# successfully saved item in redis

app = FastAPI()

@app.get("/viewItem/{item_id}")
def viewItem(item_id: int): # must validate id entered
    returnItem = None
    for item in items:
        if item.id == item_id:
            returnItem = item
    if returnItem:
        return returnItem
    return {"Error" : "Item doesn't exist"}

@app.get("/viewItems")
def viewItems(): # shows all items
    if not items:
        return {"Error" : "No Items"}
    return items

@app.post("/createItem")
def createItem(item: Item): # must hardcore id, done and timestamp fields before adding item to db
    items.append(item)
    return item

@app.post("/markItemAsDone/{item_id}")
def markItemAsDone(item_id: int):
    for item in items:
        if item.id == item_id:
            item.done = True
            return item
    return {"Error" : "Item doesn't exist"} # must return appropriate http

@app.post("/updateItemDescription/{item_id}/{desc}")
def updateItemDescription(item_id: int, desc: str):
    for item in items:
        if item.id == item_id:
            item.description = desc
            return item
    return {"Error" : "Item doesn't exist"} # must return appropriate http

@app.post("/deleteItem/{item_id}")
def deleteItem(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, regex=None)]
): # must hardcore id, done and timestamp fields before adding item to db
    deleteItem = None
    for item in items:
        if item.id == item_id:
            deleteItem = item
    if deleteItem:
        items.remove(deleteItem)
        return deleteItem
    return {"Error" : "Item doesn't exist"} # must return appropriate http

@app.post("/deleteItems")
def deleteItem(): # must hardcore id, done and timestamp fields before adding item to db
    items = [] # wipe db
    return {"Message" : "All items deleted"}

@app.get("/searchItems")
def searchByDescription(
    q: Annotated[str, Query(min_length=3, max_length=50, regex="")] # , regex='regex')] = defaultval
):
    # of course need fancier search
    for item in items:
        if item.description and (q in item.description.split()):
            return item
    return {"Message" : "No Results"}