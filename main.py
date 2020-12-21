import requests
from pprint import pprint
from os import sys

# startDate = '2019-09-27'
startDate = sys.argv[1]
phone_number = '177xxxxxxxx'
passwd = 'password'
# authentication 需要在你登录网站之后的报文里面找，不会变
authentication = '156xxxxxxxxxxxxxxxxxxxxxxx'
# 起始站的 ID
start_port_no = '1010'
# 终点站的 ID，1014 是花鸟岛（只有这个岛需要抢吧）
end_port_no = '1014'

accounts = [
    {
        'phoneNum': phone_number,
        'passwd': passwd,
        'authentication': authentication,
        'passengers': [
            # passId 是乘客的 Id，在报文里面可以找到
            {'passName': '某某某', 'credentialType': 1, 'passId': 111},
            {'passName': '某某某', 'credentialType': 1, 'passId': 222},
        ],
        'seatNeed': 2,
    },
]

for account in accounts:
    code = 0
    while code != 200:
        login_res = requests.post('https://www.ssky123.com/api/v2/user/passLogin?phoneNum=' + account['phoneNum'] + '&passwd=' + account['passwd'] + '&deviceType=2').json()
        passengers = account['passengers']

        print('===================Login Info============================')
        print(login_res)
        userid = login_res['data']['userId']
        token = login_res['data']['token']

        def get(url, params={}):
            print('GET to', url)
            token_check_res = requests.get('https://www.ssky123.com/api/v2/user/tokenCheck', headers={'authentication': authentication, 'token': token}).json()
            res = requests.get(url, headers={'authentication': account['authentication'], 'token': token}, params=params).json()
            print('Response :', res)
            print()
            return res

        def post(url, params={}):
            print('GET to', url)
            token_check_res = requests.get('https://www.ssky123.com/api/v2/user/tokenCheck', headers={'authentication': authentication, 'token': token}).json()
            res =  requests.post(url, headers={'authentication': account['authentication'], 'token': token}, json=params).json()
            print('Response :', res)
            print()
            return res

        print('===================Route Info============================')
        token_check_res = get('https://www.ssky123.com/api/v2/user/tokenCheck')
        query_ticket_res = post('https://www.ssky123.com/api/v2/line/ship/enq',
                                {
                                    'startPortNo': start_port_no,
                                    'endPortNo': end_port_no,
                                    'startDate': startDate
                                })

        route = None
        for tr in query_ticket_res['data'][::-1]:
            for s in tr['seatClasses'][::-1]:
                if s['totalCount'] >= account['seatNeed']:
                    route = tr
                    break
            if route is not None:
                break

        #  route = query_ticket_res['data'][0]
        print('\nroute:\n')
        pprint(route)
        if route is not None:
            seat = None
            for s in route['seatClasses'][::-1]:
                if s['totalCount'] >= account['seatNeed']:
                    seat = s
            print('===================Seat Info============================')
            print('\nseat:\n')
            if seat is not None:
                pprint(seat)

                orderItemRequests = []
                for p in passengers:
                    p['seatClassName'] = seat['className']
                    p['seatClass'] = seat['classNum']
                    p['freeChildCount'] = 0
                    p['realFee'] = seat['totalPrice']
                    p['ticketFee'] = seat['totalPrice']
                    orderItemRequests.append(p)
                print('===================Order Info============================')
                print(orderItemRequests)

                order = route
                order['orderItemRequests'] = orderItemRequests
                order['userId'] = userid
                order['contactNum'] = phone_number
                order['totalFee'] = seat['totalPrice'] * len(passengers)
                order['totalPayFee'] = seat['totalPrice'] * len(passengers)
                order['sailDate'] = startDate
                pprint(order)
                res = post('https://www.ssky123.com/api/v2/holding/save', order)
                code = res['code']

                post('https://www.ssky123.com/api/v2/user/loginOut')
