from pprint import pprint

##
## ORDER MATTERS: CANNOT BE CHANGED AFTER PROD DATA EXISTS
##

STAY_TYPE = ['Entire place','Private room','Shared room']
PROP_TYPE = ['House','Apartment','Bed and breakfast','Boutique hotel','Bungalow', 'Cabin','Chalet','Cottage','Guest suite','Guesthouse','Hostel','Hotel','Loft','Resort','Townhouse', 'Villa']
UNIQ_TYPE = ['Barn','Boat','Camper/RV','Campsite','Casa particular','Castle','Cave','Cycladic house','Dammuso','Dome house','Earth house','Farm stay','Houseboat','Hut','Igloo','Island','Lighthouse','Minsu','Nature lodge','Pension (South Korea)','Plane','Ryokan','Shepherdshut (U.K., France)','Tent','Tiny house','Tipi','Train','Treehouse','Trullo','Windmill','Yurt']

## THESE ARRAYS SERVE AS BITMASKS AND CANNOT HAVE MORE THAN 32 ITEMS
AMENITIES = ['Kitchen','Shampoo','Heating','A/C','Washer','Dryer','Wifi','Breakfast','Fireplace','Buzzer/wireless intercom','Doorman','Hangers','Iron','Hair dryer','Workspace','TV','Crib','High chair','Self check-in','Smoke detector']
FACILITIES = ['Free parking','Gym','Hot tub','Pool']
RULES = [('Events allowed','No events allowed'),('Pets allowed','No pets allowed'),('Smoking permitted','Smoking not permitted')]

DICTS = {}

def str_to_idx(const_list, in_str):
    if type(const_list) != list or type(in_str) != str:
        return None
    const_id_str = str(id(const_list))
    const_dict = DICTS.get(const_id_str)
    if not const_dict:
        const_dict = {}
        for i in range(len(const_list)):
            const_dict[const_list[i]] = i
        DICTS[const_id_str] = const_dict
        pprint(DICTS)
    return const_dict[in_str]

def mask_to_list(const_list, mask):
    if type(const_list) != list or type(mask) != int:
        return None
    out_list = []
    for i in range(len(const_list)):
        if mask & (1 << i):
            if id(const_list) == id(RULES):
                out_list.append(const_list[i][0])
            else:
                out_list.append(const_list[i])
        else:
            if id(const_list) == id(RULES):
                out_list.append(const_list[i][1])
    return out_list

def list_to_mask(const_list, in_list):
    if type(const_list) != list or type(in_list) != list:
        return 0
    const_id_str = str(id(const_list))
    const_dict = DICTS.get(const_id_str)
    if not const_dict:
        const_dict = {}
        bit = 1
        for elem in const_list:
            if id(const_list) == id(RULES):
                const_dict[elem[0]] = bit
                const_dict[elem[1]] = bit
            else:
                const_dict[elem] = bit
            bit = bit << 1
        DICTS[const_id_str] = const_dict
        pprint(DICTS)
    mask = 0
    for elem in in_list:
        if elem in const_dict:
            if id(const_list) == id(RULES):
                idx = const_dict[elem] >> 1
                if elem == const_list[idx][0]:
                    mask = mask | const_dict[elem]
            else:
                mask = mask | const_dict[elem]
    return mask

