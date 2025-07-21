import pandas as pd
import numpy as np
import os
import subprocess

def process_argus_full_csv(file_path, output_path):

    columns = [
        'SrcId', 'Rank', 'StartTime', 'LastTime', 'Trans', 'Flgs', 'Seq', 'Dur', 'RunTime', 'IdleTime',
        'Mean', 'StdDev', 'Sum', 'Min', 'Max',
        'SrcMac', 'DstMac', 'SrcOui', 'DstOui',
        'SrcAddr', 'DstAddr', 'Proto', 'Sport', 'Dport',
        'sTos', 'dTos', 'sDSb', 'dDSb', 'sCo', 'dCo', 'sTtl', 'dTtl', 'sHops', 'dHops',
        'sIpId', 'dIpId', 'sMpls', 'dMpls', 'AutoId',
        'sAS', 'dAS', 'iAS', 'Cause', 'NStrok', 'sNStrok', 'dNStrok',
        'TotPkts', 'SrcPkts', 'DstPkts',
        'TotBytes', 'SrcBytes', 'DstBytes',
        'TotAppByte', 'SAppBytes', 'DAppBytes', 'PCRatio',
        'Load', 'SrcLoad', 'DstLoad',
        'Loss', 'SrcLoss', 'DstLoss', 'pLoss', 'psLoss', 'pdLoss',
        'Retrans', 'SrcRetrans', 'DstRetrans', 'Pretrans', 'PsRetrans', 'PdRetrans',
        'SrcGap', 'DstGap',
        'Rate', 'SrcRate', 'DstRate', 'Dir',
        'SIntPkt', 'SIntDist', 'SIntPktAct', 'SIntActDist', 'SIntPktIdl', 'SIntIdlDist',
        'DIntPkt', 'DIntDist', 'DIntPktAct', 'DIntActDist', 'DIntPktIdl', 'DIntIdlDist',
        'SrcJitter', 'SrcJitAct', 'DstJitter', 'DstJitAct',
        'State', 'Label',
        'SUser', 'DUser', 'SrcWin', 'DstWin',
        'sVlan', 'dVlan', 'sVid', 'dVid', 'sVpri', 'dVpri',
        'SRange', 'ERange',
        'SrcTCPBase', 'DstTCPBase', 'TcpRtt', 'SynAck', 'AckDat', 'TcpOpt', 'Inode', 'Offset',
        'SMeanSz', 'DMeanSz', 'SPktSz', 'SMaxSz', 'DPktSz', 'DMaxSz',
        'SMinSz', 'DMinSz'
    ]


    numeric_cols = [
        'Dport'
    ]

    
    df = pd.read_csv(file_path, header=None, names=columns, dtype=str)

    if df.iloc[0]['StartTime'] == 'StartTime':
        df = df[1:]
 
    
    df['StartTime'] = pd.to_datetime(df['StartTime'], format='%H:%M:%S.%f')
    df['LastTime'] = pd.to_datetime(df['LastTime'], format='%H:%M:%S.%f')
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    df = df[df['Dport'] == 443]
    if df.empty:
        print("DataFrame kosong setelah filter. Periksa apakah ada Dport == 443.")
    else:
        print(f"Jumlah baris akhir: {len(df)}")


    # Tangani durasi nol atau NaN
    df['Dur'] = df['Dur'].replace(0, 0.000001).fillna(0.000001)
    df['TotPkts'] = df['TotPkts'].replace(0, 1).fillna(1)
    
    basename = os.path.basename(file_path).lower()
    if 'getbenign' in basename or 'postbenign' in basename:
        df['Traffic_Type'] = 'Benign'
    else:
        df['Traffic_Type'] = 'Malicious'

    if 'getbenign' in basename:
        df['Simulation_Scenario'] = 'benign_get_request'
    elif 'postbenign' in basename:
        df['Simulation_Scenario'] = 'benign_post_request'
    elif 'slowheader' in basename:
        df['Simulation_Scenario'] = 'slow_header_attack'
    elif 'slowbody' in basename:
        df['Simulation_Scenario'] = 'slow_body_attack'
    elif 'getflood' in basename:
        df['Simulation_Scenario'] = 'get_flood_attack'
    elif 'postflood' in basename:
        df['Simulation_Scenario'] = 'post_flood_attack'
    else:
        df['Simulation_Scenario'] = 'unknown'
    
    if 'getbenign' in basename:
        df['tool_used'] = 'get_benign'
    elif 'postbenign' in basename:
        df['tool_used'] = 'post_Benign'
    elif 'slowheader_slowhttptest' in basename:
        df['tool_used'] = 'slowhttptest_slow_header'
    elif 'slowheader_slowloris' in basename:
        df['tool_used'] = 'slowloris_slow_header'
    elif 'slowbody_slowhttptest' in basename:
        df['tool_used'] = 'slowhttptest_slow_body'
    elif 'slowbody_torshammer' in basename:
        df['tool_used'] = 'torshammer_slow_body'
    elif 'getflood_goldeneye' in basename:
        df['tool_used'] = 'goldeneye_get_flood'
    elif 'getflood_scarletddos' in basename:
        df['tool_used'] = 'scarletddos_get_flood'
    elif 'postflood_goldeneye' in basename:
        df['tool_used'] = 'goldeneye_post_flood'
    elif 'postflood_scarletddos' in basename:
        df['tool_used'] = 'scarletddos_post_flood'
    else:
        df['tool_used'] = 'unknown'

    df['StartTime'] = df['StartTime'].dt.strftime('%H:%M:%S.%f')
    df['LastTime'] = df['LastTime'].dt.strftime('%H:%M:%S.%f')


    df.to_csv(output_path, index=False)
    print(f"Dataset disimpan di: {output_path}")

input_folder = 'convertArgus'
output_folder = 'datasetResult'

for file in os.listdir(input_folder):
    if file.startswith('hasil_argus_') and file.endswith('.csv'):
        nama_lanjutan = file.replace('hasil_argus_', '').replace('.csv', '')
        input_path = os.path.join(input_folder, file)
        output_path = os.path.join(output_folder, f'Dataset_{nama_lanjutan}.csv')
        process_argus_full_csv(input_path, output_path)

print(f"Semua file pada {input_folder} telah diproses ke {output_folder}")
