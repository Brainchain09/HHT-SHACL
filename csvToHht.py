from rdflib import Graph, Literal, RDF, URIRef, XSD,  RDFS
import csv
import unit

import sys


hht="http://www.semanticweb.org/HHT_Ontology#"
oba="http://www.semanticweb.org/melodi/types#"
data="http://www.semanticweb.org/melodi/data#"

def parseHeader(firstRow) : 
    if "id" in str(firstRow[1]).lower() :
        levels=[]
        for k in range ((len(firstRow)-1)//2) :
            levels.append(firstRow[2*k+2])
        return (True, (len(firstRow)-1)//2, levels)
    else :
        levels=[]
        for k in range ((len(firstRow)-1)) :
            levels.append(firstRow[k+1])
        return (False, len(firstRow)-1, levels)

def main(filename, resultName) :

    csvfile=open(filename, newline='', encoding="utf-8")
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    basename=filename.replace(".csv", "")

    currentYear=0
    first=True
    unitDic={}
    for row in reader :
        if first :
            mode=parseHeader(row)
            for level in mode[2] :
                unitDic[level]={}
            first=False
        else : 
            date=row[0]
            if currentYear==0 :
                currentYear=date
            if currentYear!=date :
                for k in range(1, mode[1]) :
                    for nut in unitDic[mode[2][k]].values() :
                        if len(nut["geometry"])>0 :
                            nut['unit'].update(currentYear, nut["name"],nut["geometry"], nut["lower"], mode[2][k], nut["geomVersions"] )
                            nut["geometry"]=set()
                            nut["lower"]=set()
                            nut["geomVersions"]=set()
                currentYear=date
            l2=row[1]
            if mode[0] :
                nom=row[2]
            else : 
                nom=row[1] 
            ids=[]
            names=[]
            for k in range(1, mode[1]) :
                if mode[0] :
                    ids.append(row[2*k+1])
                    names.append(row[2*k+2])
                else : 
                    ids.append(row[k+1])
                    names.append(row[k+1]) 

            if l2 not in unitDic[mode[2][0]].keys() :
                unitDic[mode[2][0]][l2]=unit.unit(nom, {basename+mode[2][0] : str(l2) }, "")
                unitDic[mode[2][0]][l2].firstVersion(date, mode[2][0])
            else :
                unitDic[mode[2][0]][l2].elementUpdate( date, nom, mode[2][0])
            
            for k in range(1, mode[1]) :
                level=mode[2][k]
                if ids[k-1] not in unitDic[level].keys() :
                    unitDic[level][ids[k-1]]={"unit" :unit.unit(names[k-1], {basename+level : ids[k-1] },"") , "geometry" : set(), "lower" : set(), "geomVersions" : set(), "name" : names[k-1]}
                    unitDic[level][ids[k-1]]["unit"].firstVersion(date, level)
                unitDic[level][ids[k-1]]["geometry"].add(unitDic[mode[2][0]][l2])
                unitDic[level][ids[k-1]]["geomVersions"].add(unitDic[mode[2][0]][l2].currentVersion)
                if k==1 :
                    lowerId=l2
                    unitDic[level][ids[k-1]]["lower"].add(unitDic[mode[2][k-1]][lowerId].currentVersion)
                else : 
                    lowerId=ids[k-2]
                    unitDic[level][ids[k-1]]["lower"].add(unitDic[mode[2][k-1]][lowerId]['unit'].currentVersion)
                unitDic[level][ids[k-1]]["name"]=names[k-1]

    for k in range(1, mode[1]) :
        for nut in unitDic[mode[2][k]].values() :
            if len(nut["geometry"])>0 :
                nut['unit'].update(currentYear, nut["name"],nut["geometry"], nut["lower"], mode[2][k], nut["geomVersions"] )
                nut["geometry"]=set()
                nut["lower"]=set()
                nut["geomVersions"]=set()
    g=Graph()
    g.parse('HHT.ttl')
    g.namespace_manager.bind('hht', URIRef(hht))
    g.namespace_manager.bind('oba', URIRef(oba))
    g.namespace_manager.bind('obaData', URIRef(data))

    for d in unitDic[mode[2][0]].values() :
            d.generateRDF(g, int(currentYear), elementary=True)

    for k in range(1, mode[1]) :
        for d in unitDic[mode[2][k]].values() :
            d["unit"].generateRDF(g, int(currentYear))
    
            


    file=open(resultName, "w")
    file.write(g.serialize(format='turtle'))

if len(sys.argv)==1 :
    print("CSV filename is required")
else :
    filename=sys.argv[1]
if len(sys.argv)>2 :
    resultname=sys.argv[2]
else :
    resultname="resultGraph.ttl"
main(filename, resultname)