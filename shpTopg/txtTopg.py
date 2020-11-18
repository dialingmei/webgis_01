#!/usr/bin/python
# -*- coding:utf-8 -*-
#
#  @Filename: txtTopg.py
#  @Author: Hongmei Hu
#  @Time: 11 14 19:53 CST 2020

import psycopg2
import shptotxt as st
import csv

# connect database
def creatTable(table_name:str):
    # 多行用‘’‘
    sql1='''-- 建表
    CREATE TABLE '''+table_name+''' (
    gid serial8 primary key not null,  -- 主键ID
    name_py varchar(30), -- 拼音名称
    name_ch varchar(10), -- 中文简体名称
    name_ft varchar(10), -- 中文繁体名称
    x_coor float8, -- 中心点x坐标值
    y_coor float8, -- 中心y坐标值
    pres_loc varchar(30), -- 所在地
    type_py varchar(10), -- 建制类型拼音
    type_ch varchar(10), -- 建制类型中文简体
    lev_rank varchar(1), -- 建制等级
    beg_yr int8, -- 开始时间
    beg_rule varchar(1), -- 开始时间精度
    end_yr int8, -- 结束时间
    end_rule varchar(1), -- 结束时间精度
    note_id int8, -- 系统id
    obj_type varchar(10), -- geometry对象
    sys_id int8, -- 系统id
    geo_src varchar(20), -- geometry数据来源
    compiler varchar(10), -- 编辑人员
    geocomplr varchar(10), -- 绘制人员
    checker varchar(10), -- 审核人员
    end_data varchar(10), -- 结束时间
    beg_chg_ty varchar(12), -- 建制开始原因
    end_chg_ty varchar(12), -- 建制结束原因
    geom geometry -- geometry对象
    );'''

    cur.execute(sql1)
    conn.commit()
    print("Create table %s successful!"%(table_name))

def insertValues(table_name:str,values):
    insertSql='''
    INSERT INTO '''+table_name+'''(
    name_py,name_ch,name_ft,x_coor,y_coor,pres_loc,type_py,type_ch,lev_rank,beg_yr,beg_rule,end_yr,end_rule,
    note_id,obj_type,sys_id,geo_src,compiler,geocomplr,checker,end_data,beg_chg_ty,end_chg_ty,geom)
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    );
    '''

    temp=values[-1]
    # 从字符串到集合类型的转换
    values[-1]="st_geomfromtxt("+temp+",4326)"
    cur.execute(insertSql,values)

if __name__=='__main__':
    # 对文件夹下shp转换成txt
    path=input("请输入需入库的shp文件夹路径:")
    file = st.fileTrans()
    file.Toother(path, ".csv")
    # connect database
    conn = psycopg2.connect(database="postgis_24_sample", user="postgres", password="postgres",
                            host='10.0.0.231', port='5432')
    print("Connect database successful!")
    cur = conn.cursor()
    # 打开txt
    for fs in file.fileFind(path,'.csv'):
        csvf=csv.reader(open(fs,'r'))
        tablename=path.strip('.csv').split('/')[-1]
        creatTable(tablename)
        fields=csvf[0]
        csvf.remove(fields)
        for row in csvf:
            insertValues(tablename,row)
        for field in fields:
            # coalesce(1，2)若字段中值为1，则改为2；nullif(field,3)若字段中值为3，返回null,否则返回field当前遍历值
            cur.execute("UPDATE %s set %s=coalesce(nullif(%s,''),null);"
                        %(tablename,field,field))
        conn.commit()
        print("Table"+tablename+"import successful!")
    cur.close()
    conn.close()
