# BBC-Knowledge-Graph

## Exploration of buildng a question-answering knowledge graph based on BBC news articles. Aim is to answer questions like: "Where does Rick Wagoner work?"

## Noteable Folders:
* notebooks -> Neo4j BBC Data Load.ipynb (loads articles into Neo4j)
* scripts -> cypher_queries.cypher (queries to create the knowledge graph in Neo4j
* bbc (raw text articles from the BBC)
* bin (various binaries to support nls app)
* nls-app (Wsgi Flask application that serves queries to knowledge graph)

## Q: How does this all work?

### 1) After setup of Neo4j server, notebooks/BBC Data Load.ipynb is used to populate nodes into Neo4j
### 2) scripts/cypher_queries.cypher
