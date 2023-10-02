import csv
from .models import timeSeriesData
from datetime import datetime

filename = 'C:\\Users\\FCC\\Documents\\NITTO\\NITTO Code\\HYDRA-SAVE API SQLLITE\\hydrasaveAPI\\norm_data_clean_2.csv'
fields = []
rows = []

with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields_ = next(csvreader)
    for row in csvreader:
        rows.append(row)



print(fields_)
# print(rows[:6])

for row in rows:
    e = row[1][:10]
    d = datetime.strptime(e, '%d-%m-%Y')
    timeSeriesData.objects.create(
        date=d,
        time=datetime.now(),
        turbidity=row[3],
        sdi=row[4],
        ph=row[5],
        temperature=row[6],
        feedConc=row[7],
        permConc=row[8],
        rejectConc=0,
        feedFlow=row[9],
        permFlow=row[10],
        rejectFlow=0,
        feedPres=row[11],
        permPres=row[12],
        rejectPres=row[13],
        normSaltPassage=row[14],
        normPermFlow=row[15],
        normDP=row[16]
    )