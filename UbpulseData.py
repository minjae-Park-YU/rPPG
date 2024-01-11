import csv
import matplotlib.pyplot as plt
import pandas as pd

csv_file = 'test.csv'

# 분당 심박수 & 분당 심박수 평균
BPM = []
AverageBPM = []

with open(csv_file, newline='') as csvfile:
    csvreader = csv.reader(csvfile)

    for row in csvreader:
        if row[6] == '2':
            BPM.append(row[8])
        if row[6] == '5':
            AverageBPM.append(row[8])


# 맥파 파형
Ch1StreamLow = pd.read_csv(csv_file, low_memory=False)['9']
Ch1StreamHigh = pd.read_csv(csv_file, low_memory=False)['8']
PulseWave = Ch1StreamHigh * 256 + Ch1StreamLow

# 심박시간격
PUD1 = pd.read_csv(csv_file, low_memory=False)['6']
PUDo = pd.read_csv(csv_file, low_memory=False)['3']
HeartInterval = PUD1 * 256 + PUDo

# csv 저장
df_PulseWave = pd.DataFrame(PulseWave, columns=['Pulse Wave'])
df_HeartInterval = pd.DataFrame(HeartInterval, columns=['Heart Interval'])
df_BPM = pd.DataFrame(BPM, columns=['BPM'])
df_AverageBPM = pd.DataFrame(AverageBPM, columns=['Average BPM'])

PulseWave_csv = df_PulseWave.to_csv('Ubpulse-Pulse-Wave.csv')
HeartInterval_csv = df_HeartInterval.to_csv('Ubpulse-Heart-Interval.csv')
BPM_csv = df_BPM.to_csv('Ubpulse-BPM.csv')
AverageBPM_csv = df_AverageBPM.to_csv('Ubpulse-Avergae-BPM.csv')

# 맥파 파형 plot
plt.figure()
plt.plot(PulseWave, label='Signal', color='blue')
plt.legend()
plt.title('Signal Test')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.grid()
# plt.savefig('test.png', dpi=300)
plt.show()
