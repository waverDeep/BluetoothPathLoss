import numpy as np
import pandas as pd
import glob
import random


def make_dataset(mac_address, channel, x, y, color='r'):
    pol = []
    is_ok = True
    
    # MAC Address 문자열 검사
    if ':' in mac_address:
        mac_address = mac_address.replace(":", "-")

    # 파일 경로 설정
    if color == 'b':
        file_path = f'pointsb/{mac_address}_*_{channel}.csv'
    else:
        file_path = f'points/{mac_address}_*_{channel}.csv'

    # 파일 탐색
    file_list = glob.glob(file_path)
    file_list.sort()

    # 폴 별 데이터 추출
    # pol[0] = 0,0
    # pol[1] = 30,0
    # pol[2] = 0,30

    for index, file_name in enumerate(file_list):

        column_name = ['distance', 'rssi', 'fspl', 'channel', 'covered', 'tx_power', 
                       'tx_antenna_gain', 'rx_antenna_gain', 'tx_height',  'rx_height',
                       'tx_antenna_type', 'tx_board_type', 'x', 'y']

        data = pd.read_csv(file_name)
        data = data.values.tolist()

        pol.append(pd.DataFrame(data, columns=column_name))

    # 입력된 x,y와 같은 행을 추출
    for i in range(len(file_list)):
        pol[i] = pol[i][pol[i]['x'] == x]
        pol[i] = pol[i][pol[i]['y'] == y]

    # 20개의 행을 추출
    for i in range(len(file_list)):
        max_index = len(pol[i].index) - 20
        if max_index < 0:
            is_ok = False
            print('데이터를 생성할 수 없습니다.')
            break
        else :         
            random_index = random.randint(0, max_index)
            pol[i] = pol[i].loc[random_index:random_index+19]
            pol[i] = pol[i].reset_index(drop=True)

    # csv 저장
    if is_ok:
        for i in range(len(file_list)):
            csv_name = mac_address + f'_{channel}_{x}_{y}_pol{i+1}.csv'
            file_save_path = 'test_point_{}_{}/{}'.format(x, y, csv_name)
            # file_save_path = 'test_point_00_15/'+ csv_name
            temp = pol[i]
            temp = temp.drop(['distance', 'x', 'y'], axis=1)
            temp.to_csv(file_save_path, header=None, index=None)
            print(csv_name + '파일 생성 완료!')


make_dataset('fb-f8-c9-9d-d8-d6', 37, 0, 15, 'r')



