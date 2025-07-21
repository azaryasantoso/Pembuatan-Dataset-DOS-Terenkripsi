import os
import subprocess

input_folder = 'argusResult'
output_folder = 'convertArgus'

os.makedirs(output_folder, exist_ok=True)

ra_command_template = (
    "ra -r '{input_path}' -s srcid rank stime ltime trans flgs seq dur runtime idle mean stddev sum min max smac dmac soui doui saddr daddr proto sport dport stos dtos sdsb ddsb sco dco sttl dttl shops dhops sipid dipid smpls dmpls autoid sas das ias cause nstroke snstroke dnstroke pkts spkts dpkts bytes sbytes dbytes appbytes sappbytes dappbytes pcr load sload dload loss sloss dloss ploss sploss dploss retrans sretrans dretrans pretrans spretrans dpretrans sgap dgap rate srate drate dir sintpkt sintdist sintpktact sintdistact sintpktidl sintdistidl dintpkt dintdist dintpktact dintdistact dintpktidl dintdistidl sjit sjitact sjitidle djit djitact djitidle state label suser duser swin dwin svlan dvlan svid dvid svpri dvpri srng erng stcpb dtcpb tcprtt synack ackdat tcpopt inode offset smeansz dmeansz spktsz smaxsz dpktsz dmaxsz sminsz dminsz -n -c ',' > '{output_path}'"
)



for file in os.listdir(input_folder):
    if file.endswith('.argus'):
        base_name = file.replace('capture_', '').replace('.argus', '')
        
        input_path = os.path.join(input_folder, file)
        output_filename = f'hasil_argus_{base_name}.csv'
        output_path = os.path.join(output_folder, output_filename)

        ra_command = ra_command_template.format(input_path=input_path, output_path=output_path)
        print(f"Memproses: {file}")
        subprocess.run(ra_command, shell=True)

print("Semua file .argus berhasil dikonversi ke CSV.")
