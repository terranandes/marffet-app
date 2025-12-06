#! ../.venv/bin/python3
import sys
import pandas as pd
import re

help_msg ='\
Usage: pandas_stock.py [end_year]\n\
For example:\n\
pandas_stock.py 2025\
'
end_year_in = 2025
if (len(sys.argv) > 1 and sys.argv[1] == '-h') or len(sys.argv) > 2:
    print(help_msg)
    exit()

if len(sys.argv) == 2:
    try:
        end_year_in = int(sys.argv[1])
    except:
        print("Input end_year is not a valid integer!")

#USER modifiable CFG
lasting_yrs = 3
std_grd = 20
df = pd.read_csv('stock_list_s2006e'+str(end_year_in)+'_unfiltered.csv')

#drop column bah and bal
drop_roi_type = ['bah', 'bal']
drop_roi_cl = ['s'+'2006'+'e'+str(ey)+ roit for ey in range(2007, end_year_in+1) for roit in drop_roi_type]
df2 = df.drop(drop_roi_cl, axis=1)

#drop column unused yrs
drop_yrs_cl = ['s'+'2006'+'e'+str(ey)+'yrs' for ey in range(2007, end_year_in)]
df3 = df2.drop(drop_yrs_cl, axis=1)

#Filter stock with lasting years > lasting_yrs
df3_filtering_col = 's2006e'+str(end_year_in)+'yrs'
#df4 = df3[df3.s2006e2025yrs > lasting_yrs]
df4 = df3[df3[df3_filtering_col] > lasting_yrs]

#sorted by 's2006e'+str(end_year_in)+'bao' , TBD with variable
df5=df4.sort_values(by='s2006e'+str(end_year_in)+'bao', ascending=False)

#filter valid stock info only
vslist = []
for stk in df5.index:
    #tmp2 = int(df5.loc[stk][-1])
    tmp2 = int(df5.loc[stk].iat[-1])
    if tmp2 >= 15 :
        vs = True
    else :
        #vs = pd.isnull(df5.loc[stk][-1-tmp2-1])
        vs = pd.isnull(df5.loc[stk].iat[-1 - tmp2 - 1])
    vslist.append(vs)
df6 = df5[vslist]

#filter stock with std less than std_grd
vslist_2 = []
for stk2 in df6.index:
    #tmp2 = int(df6.loc[stk2][-1])
    tmp2 = int(df6.loc[stk2].iat[-1])
    if tmp2 >= 15 :
        #ser_s = df6.loc[stk2][4:-1]
        ser_s = df6.loc[stk2].iloc[4:-1]
    else :
        #ser_s = df6.loc[stk2][-1-tmp2:-1]
        ser_s = df6.loc[stk2].iloc[-1-tmp2:-1]
    if ser_s.std() <= std_grd : 
        vs_2 = True
    else :
        vs_2 = False
    vslist_2.append(vs_2)
df7 = df6[vslist_2]

#filter special ETF with id 'L'
vslist_3 = []
for stk3 in df7.index:
    #id = df7.loc[stk3][0]
    id = df7.loc[stk3].iat[0]
    if re.search("L", id) :
        vs_3 = False
    else :
        vs_3 = True
    vslist_3.append(vs_3)

df8 = df7[vslist_3]

df8.to_csv('stock_list_s2006e'+str(end_year_in)+'_filtered.csv')

