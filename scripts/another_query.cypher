MATCH (s:Sentence)-[:SENTENCE_TAG_OCCURRENCE]->(root:TagOccurrence)
WHERE root.value = "work"

WITH s, root

MATCH (:Sentence)-[:SENTENCE_TAG_OCCURRENCE]-(:TagOccurrence)-[:NSUBJ]->(e1:TagOccurrence {ne: ["PERSON"]})<-[r1:DEP]-(root)-[r2:DEP]-> (:Sentence)-[:SENTENCE_TAG_OCCURRENCE]-(:TagOccurrence)-[:OBJ]-(e2:TagOccurrence {ne: ["ORGANIZATION"]})

RETURN e1