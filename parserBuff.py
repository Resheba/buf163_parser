from time import sleep
import requests, json
from cookie import cookies


PAGE_DELAY = 1
UPDATE_DELAY = 5

def getItemPrice(name):
    url = f'https://buff.163.com/api/market/goods?game=csgo&search={name}'
    sleep(PAGE_DELAY)
    response = requests.get(url, cookies=cookies)
    jsonResp = json.loads(response.text)
    try:
        price = jsonResp.get('data').get('items')[0].get('sell_min_price')
    except:
        print('No stiker price')
        return 0
    return float(price)

def getItemInfo(id, minPrice, sti_ids: list):
    url = f'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={id}&sort_by=created.desc&extra_tag_ids={",".join(sti_ids)}'
    sleep(PAGE_DELAY)
    response = requests.get(url, cookies=cookies)
    jsonResp = json.loads(response.text)
    item = jsonResp.get('data').get('items')[0]

    priceLot = item.get('price')
    name = jsonResp.get('data').get('goods_infos').get(str(id)).get('name')
    link = 'https://buff.163.com/goods/'+str(id)+f'#sort_by=created.desc&extra_tag_ids={",".join(sti_ids)}'
    stikers = []

    stikersJson = item.get('asset_info').get('info').get('stickers')

    for stiker in stikersJson:
        stikWear = stiker.get('wear')
        stikName = stiker.get('name')
        stikPrice = getItemPrice(stikName)
        stikers.append(dict(stikWear=stikWear, stikName=stikName, stikPrice=stikPrice))
    print('----', name, 'Цена лота: '+priceLot, 'Мин. цена: '+minPrice, link, f'Стикеры: {stikers}', sep='\n')

def getSkinsByStikers(sti_ids: list):
    sti_ids = [str(i) for i in sti_ids]
    skinsDict = {}
    url = f'https://buff.163.com/api/market/goods?game=csgo&extra_tag_ids={",".join(sti_ids)}'

    response = requests.get(url, cookies=cookies)
    #print(response.text[:50])
    jsonResp = json.loads(response.text)
    total_page = jsonResp.get('data').get('total_page')

    for page in range(1,total_page+1):
        if page != 1:
            newPage = url + '&page_num=' + str(page)
            sleep(PAGE_DELAY)
            response = requests.get(newPage, cookies=cookies)
            jsonResp = json.loads(response.text)

        data = jsonResp.get('data')
        items = data.get('items')

        for item in items:
            sellNum = item.get('sell_num')
            id = item.get('id')
            skinsDict[id] = sellNum
    return skinsDict

def checkUpdates(sti_ids: list, skinsDict: dict):
    sti_ids = [str(i) for i in sti_ids]
    url = f'https://buff.163.com/api/market/goods?game=csgo&extra_tag_ids={",".join(sti_ids)}'

    response = requests.get(url, cookies=cookies)
    #print(response.text[:50])
    jsonResp = json.loads(response.text)
    total_page = jsonResp.get('data').get('total_page')

    for page in range(1,total_page+1):
        if page != 1:
            newPage = url + '&page_num=' + str(page)
            sleep(PAGE_DELAY)
            response = requests.get(newPage, cookies=cookies)
            jsonResp = json.loads(response.text)

        data = jsonResp.get('data')
        items = data.get('items')

        for item in items:
            sellNum = item.get('sell_num')
            id = item.get('id')
            if skinsDict.get(id):
                if skinsDict[id] < sellNum:
                    print(f'| New Changes: ({id}) {skinsDict[id]} => {sellNum}')
                    getItemInfo(id, item.get('sell_min_price'), sti_ids)
            else:
                print(f'| New Changes: new id: ({id})')
                getItemInfo(id, item.get('sell_min_price'), sti_ids)
            skinsDict[id] = sellNum


    




if __name__ == '__main__':
    while 1:
        try:
            stickersIds = [15861] # Stickers Ids - Здесь можно указать любые стикеры.
            sleep(UPDATE_DELAY)
            skinsDict = getSkinsByStikers(stickersIds)
            while 1:
                sleep(UPDATE_DELAY)
                print('-Start new update-')
                checkUpdates(stickersIds, skinsDict=skinsDict)
                print('-Checked-')
        except Exception as ex:
            print(ex)

#Первая загрузка - самая долгая.
