#!/usr/bin/python
# -*- coding:utf-8 -*-
#
#  @Filename: shptotxt.py
#  @Author: Hongmei Hu
#  @Time: 11 13 17:35 CST 2020

try:
    from osgeo import ogr,gdal
except:
    import ogr,gdal

import os,csv

class fileTrans:
    # 遍历文件中所有shp
    def fileFind(self,file_path,suffix:str):
        arr=[]
        for root,dirs,files in os.walk(file_path):
            # root 当前正在遍历的地址 dirs，files list 文件夹下所有目录的名字/文件（不包括子目录）
            for f in files:
                # splitext()返回路径名和文件扩展名
                sf=os.path.splitext(f)[1]
                print(sf)
                if sf==suffix:
                    arr.append(f)
        return arr

    def readShp(self,shp):
        # 支持中文路径
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","YES")
        # 属性表字段支持中文
        gdal.SetConfigOption("SHAPE_ENCODING","UTF-8")
        # 注册所有驱动
        ogr.RegisterAll()
        # 打开data
        dataS = ogr.Open(shp)
        # 获取该数据源中图层个数，一般shp数据图层只有一个。mdb,dxf等图层会有多个
        lyCount=dataS.GetLayerCount()
        # 获取第一个图层
        oLayer = dataS.GetLayerByIndex(0)
        # 图层初始化
        oLayer.ResetReading()
        # 获取图层中属性表表头并输出，可以定义建表语句
        print("属性表信息：")
        # 获取schema information,OGRFeatureDefn
        oDefn=oLayer.GetLayerDefn()
        # 获取字段数
        iFieldCount=oDefn.GetFieldCount()
        arrayF=[]
        for i in range(len(iFieldCount)):
            # 获取对应i的字段FieldDefn
            oField=oDefn.GetFieldDefn(i)
            print("%s:%s(%d,%d)"%(
            # 获取对应字段的name
            oField.GetNameRef(),
            # 返回OGRFieldType type  fType=oField.GetType()
            # 返回char
            oField.GetFieldTypeName(oField.GetType()),
            # 返回int
            oField.GetWidth(),
            oField.GetPrecision()))
            # fetch field name
            arrayF.append(oField.GetNameRef())
        arrayF.append('geom')
        # feature number
        iFeatureCount=oLayer.GetFeatureCount(0)
        print(iFeatureCount)
        # fetch next feature
        oFeature=oLayer.GetNextFeature()
        result=[]
        result.append(arrayF)
        while oFeature is not None:
            # 清空list
            arrayF.clear()
            # fetch the content of attribute table
            for i in range(len(iFeatureCount)):
                # fetch field value(string)
                arrayF.append(oFeature.GetfieldAsString)
                if i==1: print(result)  #test
            # fetch geometry(object)
            oGeometry=oFeature.GetGeometryRef()
            arrayF.append(str(oGeometry))
            result.append(arrayF)

            oFeature = oLayer.GetNextFeature()

        return result

    # *对应列表，**对应字典
    def Toother(self,file_path,suf:str):
        suffix1='.shp'
        for sP in self.fileFind(file_path,suffix1):
            tPath=os.path.splitext(sP)[0]+suf
            if suf=='.txt':
                with open(tPath,'w',encoding='utf-8') as file:
                    for line in self.readShp(sP):
                        for l in line:
                            file.write(l+'\t') # 制表符：对齐表格各列
                        file.write('\n') # 换行（下一个要素信息）
            if suf=='.csv':
                # newline：避免空行
                with open(tPath,'w',newline='') as file:
                    csvWriter=csv.writer(file)
                    for line in self.readShp(sP):
                        csvWriter.writerow(line)
