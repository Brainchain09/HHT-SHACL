from rdflib import Graph, Literal, RDF, URIRef, XSD,  RDFS

def createObject(prefix,text) :
    final=text.replace(" ", "_").replace("(", "").replace(")", "")
    return URIRef(prefix+final)


hht="http://www.semanticweb.org/HHT_Ontology#"
oba="http://www.semanticweb.org/melodi/types#"
data="http://www.semanticweb.org/melodi/data#"


isAnnee=URIRef('http://www.w3.org/2006/time#inXSDgYear')
hasBeginning=URIRef('http://www.w3.org/2006/time#hasBeginning')
hasEnd=URIRef('http://www.w3.org/2006/time#hasEnd')


def intersect(start1, start2, end1, end2):
    return (end1<=end2 and end1>=start2) or (start1<=end2 and start1>=start2)
def idObardi(niveau, id) :
    return niveau+str(id).rjust(6, "0")

def addDate(toAdd, startDate, endDate, uriV) :
    gyearStart = Literal(str(startDate), datatype=XSD.gYear)
    gyearEnd=Literal(str(endDate), datatype=XSD.gYear)
    InstantDebut=URIRef('http://www.semanticweb.org/melodi/data#year'+str(startDate))
    InstantFin=URIRef('http://www.semanticweb.org/melodi/data#year'+str(endDate))
    toAdd.add((InstantDebut, isAnnee, gyearStart))
    toAdd.add((InstantFin, isAnnee, gyearEnd))
    Duree=URIRef('http://www.semanticweb.org/melodi/data#duree'+str(startDate)+'-'+str(endDate))
    toAdd.add((Duree, hasEnd, InstantFin))
    toAdd.add((Duree, hasBeginning, InstantDebut))
    toAdd.add((uriV, URIRef('http://www.semanticweb.org/HHT_Ontology#validityPeriod'), Duree))


class unit :
    def __init__(self, nameI, ids,domain, uri="") :
        self.name=nameI
        self.ids=ids
        self.currentVersion=None
        self.version=[]
        self.domain=domain
        if uri=="" :
            uriBase=domain
            for id in ids.keys():
                uriBase+=str(id)+str(ids[id])
            self.uri=createObject(data, uriBase)
            self.uriBase=uriBase
        else :
            self.uri=uri
            self.uriBase=uri.split("#")[1]



    def firstVersion(self, date, level) :
        ver=version(self.name, date, level, self.uriBase)
        self.currentVersion=ver

    def elementUpdate(self, date, name, level) :
        if name=="" :
            nameUse=self.currentVersion.name
        else :
            nameUse=name
        if nameUse!=self.currentVersion.name or level!=self.currentVersion.level :
            self.currentVersion.endDate=date
            self.version.append(self.currentVersion)
            self.currentVersion=version(nameUse, date, level, self.uriBase)
        self.currentVersion.endDate=date


    def update(self, date, name, geometry, lower, level, geomVer) :
        if name=="" :
            name=self.currentVersion.name
        if len(self.currentVersion.geometry)>0 :
            if (name!=self.currentVersion.name or geometry!=self.currentVersion.geometry or level!=self.currentVersion.level)  :
                self.currentVersion.endDate=date
                self.version.append(self.currentVersion)
                self.currentVersion=version(name, date, level, self.uriBase)
                self.currentVersion.geometry=geometry
        else : 
            self.currentVersion.geometry=geometry
        self.currentVersion.lower=self.currentVersion.lower.union(lower)
        self.currentVersion.elementaryVersions=self.currentVersion.elementaryVersions.union(geomVer)
        self.currentVersion.endDate=date


    def geometry(self, date):
        if date>=self.currentVersion.startDate and date<self.currentVersion.endDate :
            return self.currentVersion.geometry
        else :
            for version in self.version :
                if date>=version.startDate and version.endDate :
                    return version.geometry
        return {}

    def generateRDF(self, g, endDate, elementary=False) :
                g.add((self.uri, RDFS.label, Literal(self.name)))
                g.add((self.uri, RDF.type, createObject(hht, "Unit")))
                for id in self.ids.keys() :
                    g.add((self.uri, createObject(hht, "hasID"), createObject(data, self.uriBase+"_ID"+str(id))))
                    g.add((createObject(data, self.uriBase+"_ID"+str(id)), createObject(hht, "isFrom"),createObject(data, "base"+str(id))))
                    g.add((createObject(data, self.uriBase+"_ID"+str(id)), RDF.type,createObject(hht, "outerID")))
                    g.add((createObject(data, "base"+str(id)), RDF.type,createObject(hht, "IDSource")))
                    g.add((createObject(data, self.uriBase+"_ID"+str(id)), createObject(hht, "idValue"),Literal(self.ids[id])))
                g.add((self.uri, createObject(hht, "hasVersion"), self.currentVersion.uri))
                if (self.currentVersion.endDate==endDate) :
                    self.currentVersion.endDate=endDate+1
                self.currentVersion.generateRDF(g, elementary=elementary)
                for v in self.version :
                    g.add((self.uri, createObject(hht, "hasVersion"), v.uri))
                    v.generateRDF(g, elementary=elementary)

    def coherentRetroactiveNaming(self, name, start, end) :
            if intersect(start, self.currentVersion.startDate, end,self.currentVersion.endDate) :
                self.currentVersion.name=name
            for version in self.version :
                if intersect(start, version.startDate, end, version.endDate) :
                    self.currentVersion.name=name
    
    def coherentRetroactiveFirstVersion(self, date, level) :
        ver=version(self.name, date, level, self.uriBase)
        self.currentVersion=ver
    





class version :
    def __init__(self, nameI, startDate, level, uriBase) :
        self.name=nameI
        self.startDate=startDate
        self.endDate=startDate
        self.level=level
        self.lower=set()
        self.geometry=set()
        self.elementaryVersions=set()
        self.uri=createObject(data, uriBase+str(startDate))
    def generateRDF(self, g, elementary=False) :
        g.add((self.uri, RDFS.label, Literal(self.name)))
        g.add((self.uri, RDF.type, createObject(hht, "UnitVersion")))
        addDate(g, self.startDate, self.endDate, self.uri)
        g.add((self.uri, createObject(hht, "isMemberOf"), createObject(oba, self.level)))
        if elementary :
            g.add(( createObject(oba, self.level), RDF.type, createObject(hht, "ElementaryLevelVersion")))
        g.add((createObject(oba, self.level), RDF.type, createObject(hht, "LevelVersion")))
        for e in self.lower : 
            g.add((self.uri, createObject(hht, "hasSubUnit"), e.uri))
        for e in self.elementaryVersions : 
            g.add((self.uri, createObject(hht, "contains"), e.uri))
        
