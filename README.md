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

