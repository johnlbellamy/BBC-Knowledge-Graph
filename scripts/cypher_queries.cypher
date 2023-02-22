
#Setup:

CREATE CONSTRAINT ON (n:AnnotatedText) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:Tag) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:Sentence) ASSERT n.id IS UNIQUE;
CREATE INDEX ON :Tag(value);

###################################################################

CALL ga.nlp.config.setDefaultLanguage('en')

###################################################################

CALL ga.nlp.processor.addPipeline({textProcessor: 'com.graphaware.nlp.processor.stanford.StanfordTextProcessor', name: 'nerPipeline', processingSteps: {tokenize: true, ner: true, dependency: true}, stopWords: '+,result, all, during', 
threadNumber: 20})

#####################################################################

CALL apoc.periodic.iterate(
'MATCH (n:Article) RETURN n',
'CALL ga.nlp.annotate({
        	text: n.Text,
        	id: id(n),
        	pipeline: "nerPipeline",
        	checkLanguage:false
})
YIELD result MERGE (n)-[:HAS_ANNOTATED_TEXT]->(result)',
{batchSize:1, iterateList:false})

###################################################################

MATCH (o:NE_Organization)-[]-(p:NE_Person)-[]-(t:TagOccurrence)
WHERE NOT t:NE_Person AND t.pos IN [['NN']]
//DISTINCT p.value AS Person, collect(distinct t.value) as Title, o.value AS Company

WITH DISTINCT p.value AS P, o.value AS C

MERGE (:Person {value:P})-[:WORKS_FOR]-(:Company {value:C})

##################################################################

MATCH (l:NE_Location)-[]-(p:NE_Person)-[]-(t:TagOccurrence)
RETURN DISTINCT p.value AS Person, l.value AS Location


##################################################################

MATCH (l:NE_Location)-[]-(p:NE_Person)-[]-(t:TagOccurrence)
//WHERE NOT t:NE_Person AND t.pos IN [['NN']]
WITH DISTINCT p.value AS P, l.value AS L
MERGE (:Person {value:P})-[:LIVES_IN]-(:Location {value:L})

###################################################################

MATCH (o:NE_Organization)-[]-(p:NE_Person)-[]-(t:TagOccurrence)
WHERE NOT t:NE_Person AND t.pos IN [['NN']]
WITH DISTINCT p.value AS Person, collect(distinct t.value) as Title, o.value AS Company
ORDER BY Company
MERGE (:Person {value:Person})-[:HAS_TITLE]-(:Title {value:Title})


#######################################################################

MATCH (s:Sentence)-[:HAS_TOKEN_OCCURRENCE]->(root:TokenOccurrence)
WHERE root.lemma = "work"

WITH s, root

MATCH (e1:TokenOccurrence {ne: ["PERSON"]})<-[r1:DEP]-(root)-[r2:DEP]-> (e2:TokenOccurrence {ne: ["ORGANIZATION"]})
WHERE r1.type = 'nsubj' AND r2.type = 'obl:for'

WITH e1, e2
MATCH (e1)-[:REFERS_TO]->(ef1:Entity)
MATCH (e2)-[:REFERS_TO]->(ef2:Entity)

RETURN ef1.value AS entity1, ef1.ne AS type1, "WORKS_FOR" AS relation, ef2.value AS entity2, ef2.ne AS type2
