# HHT-SHACL
HHT (Hierarchical Historical Territories) is an ontology designed to describe multiple-hierarchy evolving territories in an historical context. This ontology relies on a discrete geometry description using building blocks. It is provided with an algorithm implemented with SHACL-Rules to detect and categorize changes inside a knowledge graph relying on HHT. 

## HHT Ontology

The file **HHT.ttl** contains the HHT ontology description.

## HHT-SHACL algorithm

Two version of the HHT-SHACL algorithm are provided in this repository :

 - The basic HHT-SHACL implementation is contained inside the **HHT-SHACL.shacl** file.
 - An improvement on the first version, named HHT-SHACL-FDD (for Flawed Data Detection) is also provided. It is designed to point out potentially inconsistent changes detected due to missing data in the building blocks description.

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

