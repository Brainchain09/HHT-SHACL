# HHT-SHACL
HHT (Hierarchical Historical Territories) is an ontology designed to describe multiple-hierarchy evolving territories in an historical context. This ontology relies on a discrete geometry description using building blocks. It is provided with an algorithm implemented with SHACL-Rules to detect and categorize changes inside a knowledge graph relying on HHT. 

## HHT Ontology

The file **HHT.ttl** contains the HHT ontology description.

## HHT-SHACL algorithm

Two version of the HHT-SHACL algorithm are provided in this repository :

 - The basic HHT-SHACL implementation is contained inside the **HHT-SHACL.shacl** file.
 - An improvement on the first version, named HHT-SHACL-FDD (for Flawed Data Detection) is also provided. It is designed to point out potentially inconsistent changes detected due to missing data in the building blocks description.

## Converting data and using the algorithm

We provide a python script (**csvToHht.py**) to convert data inside a .csv file to a HHT knowledge graph. The CSV file should respect a fixed structure. Delimiters should be '**,**' and quote characters should be '**"**'. First line of the csv should respect the following format :

|Year  |Id Building Block (Level 0)  | Level 0 |  Id Upper 1 | Level 1 |...|Id Upper n | Level n|
|--|--|--|--|--|--|--|--|

ID columns should contain territories Ids, while the level * (which should be replaced by the actual level name, such as NUTS3 for example) columns should contain the names of the territories. Note that it is possible to avoid the use of IDs and use only name columns. In that case, the script will consider that the names are to be used as identifiers. To do so, the second column's first line should not contain "ID". 
Finally, note that each building block should be described for each year it exists, and the lines should be sorted  by year. The table below provides a simple example for two building blocks.

|Year  |Id Commune  | Commune |  Id Departement | Departement |
|--|--|--|--|--|
|1987|31600|Muret|31|Haute-Garonne|
|1987|31000|Toulouse|31|Haute-Garonne|
|1988|31600|Muret|31|Haute-Garonne|
|1988|31000|Toulouse|31|Haute-Garonne|
|1989|31600|Muret|31|Haute-Garonne|
|1989|31000|Toulouse|31|Haute-Garonne|

To run the script one can use the following command, assuming the **HHT.ttl** is located in the same directory as **csvToHht.py** :

    python csvToHht.py <csvFileName.csv> <targetFile.ttl>
   
  Where <csvFileName.csv> and <targetFile.ttl> should be replaced with the data source file and the path where the result file is to be created. Note that the target file is optional. If none is provided, it will create a file titled **resultGraph.ttl**.

Note that in order to use the algorithm on the resulting graph, it is necessary to first edit the **.shacl** file by replacing the dates at lines 118 and 153, respectively by the earliest and latest dates inside your CSV file.

## Datasets

Examples of knowledge graphs using HHT are provided. They are located in the folders :

 - FranceRegion+NUTS
 - FranceRegions
 - NUTS
 - Third Republic

Every dataset folder contains a **.ttl** file containing the initial knowledge graph, the result of the FDD version of the algorithm on this graph (**resultAlgo.ttl**) a dataset description and, when pertinent, the original datasets used to create the knowledge graphs.

## Querying

We provide example of SPARQL queries that can be used in order to query the knowledge graph and the result of the algorithm.

 1. Count the territories described and their version by level : 

	    SELECT DISTINCT ?Level (COUNT(DISTINCT ?version) AS ?versionCount) (COUNT(DISTINCT ?unit) AS ?unitCount) 
	    WHERE{
	        ?version hht:isMemberOf ?Level.
	        ?unit hht:hasVersion ?version.
	    } GROUP BY ?Level

 2. Count feature changes occurring per year  :
 

	    SELECT DISTINCT ?year (COUNT(DISTINCT ?change) AS ?changeCount) WHERE{
    	    {
    		    ?change a hht:FeatureChange.
    		     ?change hht:before ?version.
    		    ?version hht:validityPeriod ?interval.
    		    ?interval <http://www.w3.org/2006/time#hasEnd> ?start.
    		    ?start <http://www.w3.org/2006/time#inXSDgYear> ?year.
    		} UNION {
    		    ?change a hht:Appearance.
    		    ?change hht:after ?version.
    		    ?version hht:validityPeriod ?interval.
    		    ?interval <http://www.w3.org/2006/time#hasBeginning> ?start.
    		    ?start <http://www.w3.org/2006/time#inXSDgYear> ?year.
    	    }
        } GROUP BY ?year ORDER BY ?year

 3. Count composite changes occurring per year  :

	    SELECT ?year (COUNT(DISTINCT ?change) AS ?changeCount)WHERE{
	    	?change a hht:CompositeChange.
	    	?changeF hht:isPartOf ?change.
	    	?changeF hht:before ?version.
	    	?version hht:validityPeriod ?interval.
	    	?interval time:hasEnd ?start.
	    	?start <http://www.w3.org/2006/time#inXSDgYear> ?year.
	    } GROUP BY ?year ORDER BY ?year

## Querying : comparison with TSN

Some queries can be carried out in TSN and not in HHT. Here are some examples :

1. Identify levels taking part in several hierarchies :

		SELECT DISTINCT ?level WHERE {
			{SELECT ?level (COUNT(DISTINCT ?hierarchy) AS ?nbHierarchies) {
				?level a hht:Level.
				?level hht:hasVersion ?v.
				?v hht:isLevelOf ?hierarchy.	
			} GROUP BY ?level.}
			FILTER (?hierarchy > 1).	
		}

2. Identify Units that are part of given territories from different hierarchies :

		SELECT DISTINCT ?unit WHERE {
			?unit a hht:Unit.
			?unit hht:hasUnitVersion ?v.
			?v hht:isMemberOf ?levelV.
			oba:Paroisse hht:hasLevelVersion ?levelV.
			oba:Generalite000007v1 hht:contains ?v.
			oba:Diaconne000106v1 hht:contains ?v.	
		}
		
Some queries easily written in TSN get extremely verbose with HHT. For example if we want to get all the units being part of oba:Generalite000007 at the same time as oba:Paroisse015267, it will be written in TSN : 

		SELECT DISTINCT ?unit WHERE {
			?unit a tsn:Unit.
			?unit tsn:hasVersion ?v.
			?v tsn:isMemberOf ?levelV.
			?levelV tsn:isDivisionOf ?nomenclature.
			oba:Generalite000007 tsn:hasVersion ?generalV.
			oba:Paroisse015267 tsn:hasVersion ?vParoisse.
			?generalV tsn:hasSubFeature ?vParoisse.
			?generalV tsn:hasSubFeature ?v.
		}
It is much more verbose in HHT :

		SELECT DISTINCT ?unit WHERE {
			?unit a hht:Unit.
			?unit hht:hasUnitVersion ?v.
			oba:Generalite000007 hht:hasUnitVersion ?generalV.
			?generalV hht:hasSubUnit ?v.
			{SELECT ?datestart ?dateend WHERE{
				oba:Paroisse015267 hht:hasVersion ?vParoisse.
				?generalV hht:hasSubUnit ?vParoisse.
				?generalV hht:validityPeriod ?gInterval.
				?gInterval time:hasBeginning ?gBegin.
				?gBegin time:inXSDgYear ?gBeginYear.
				?gInterval time:hasEnd ?gEnd.
				?gEnd time:inXSDgYear ?gEndYear.
				?vParoisse hht:validityPeriod ?pInterval.
				?pInterval time:hasBeginning ?pBegin.
				?pBegin time:inXSDgYear ?pBeginYear.
				?pInterval time:hasEnd ?pEnd.
				?pEnd time:inXSDgYear ?pEndYear.
				BIND(IF(?pBeginYear < ?gBeginYear, ?gBeginYear, ?pBeginYear) AS ?datestart)
				BIND(IF(?pEndYear > ?gEndYear, ?gEndYear, ?pENdYear) AS ?dateend)		
			}
			{SELECT ?datestartV ?dateendV WHERE{
				?generalV hht:validityPeriod ?gInterval.
				?gInterval time:hasBeginning ?gBegin.
				?gBegin time:inXSDgYear ?gBeginYear.
				?gInterval time:hasEnd ?gEnd.
				?gEnd time:inXSDgYear ?gEndYear.
				?v hht:validityPeriod ?pInterval.
				?pInterval time:hasBeginning ?pBegin.
				?pBegin time:inXSDgYear ?pBeginYear.
				?pInterval time:hasEnd ?pEnd.
				?pEnd time:inXSDgYear ?pEndYear.
				BIND(IF(?pBeginYear < ?gBeginYear, ?gBeginYear, ?pBeginYear) AS ?datestartV)
				BIND(IF(?pEndYear > ?gEndYear, ?gEndYear, ?pENdYear) AS ?dateendV)		
			}
			FILTER((?datestartV >= ?datestart && ?datestartV <= ?dateend) ||(?dateendV >= ?datestart && ?dateendV <= ?dateend)
		}

Still, the opposite is true for some queries. If we want to query for a list of all the actual changes occuring at a specific date, in TSN it will be written :

		SELECT DISTINCT ?date WHERE {
			oba:versionA tsn:isMemberOf ?levelV.
			?levelV tsn:isDivisionOf ?nomenclatureV.
			oba:versionA tsn:isVersionOf ?A.
			?nomenclatureV tsn:referencePeriod ?intervalA.
			?intervalA time:hasEnd ?endA.
			?endA time:inXSDgYear ?endDateA.
			?nomenclatureV tsn:isVersionOf ?nomenclature.
			?nomenclature tsn:hasVersion ?otherV.
			?otherV tsn:referencePeriod ?intervalOther.
			?intervalOther time:hasBeginning ?beginOther.
			?beginOther time:inXSDgYear ?date.
			FILTER (?date >= ?endDateA)
			?A tsn:hasVersion ?aV.
			?aV tsn:isMemberOf ?levelaV.
			?levelaV tsn:isDivisionOf ?otherV.
			oba:versionA tsn:hasGeometry ?geoA.
			?aV tsn:hasGeometry ?geoAv.
			FILTER(?aV != ?geoAv).
			oba:versionA tsn:hasName ?nameA.
			?aV tsn:hasName ?nameAv.
			FILTER(?nameA != ?nameAv).
		} ORDER BY ?date LIMIT 1

While in HHT it can be expressed as :


		SELECT DISTINCT ?date WHERE {
			oba:versionA hht:hasNextVersion ?nV.
			oba:versionA hht:validityPeriod ?Interval.
			?Interval time:hasEnd ?end.
			?end time:inXSDgYear ?date.
		}
