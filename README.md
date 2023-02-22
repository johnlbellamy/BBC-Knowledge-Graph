# BBC-Knowledge-Graph

## Exploration of buildng a question-answering knowledge graph based on BBC news articles. Aim is to answer questions like: "Where does Rick Wagoner work?"

## Noteable Folders:
* notebooks -> Neo4j BBC Data Load.ipynb (loads articles into Neo4j)
* scripts -> knowledge_graph.cypher (queries to create the knowledge graph in Neo4j
* bbc (raw text articles from the BBC)
* bin (various binaries to support nls app)
* nls-app (Wsgi Flask application that serves queries to knowledge graph)

## Q: How does this all work?

### 1) After setup of Neo4j server, notebooks/BBC Data Load.ipynb is used to populate nodes into Neo4j
### 2) scripts/knowledge_graph.cypher is ran in Neo4j Browser to use POS tagging from Stanford NLP to graph to answer questions baout where people live and work. 
### 3)The nlp-app is deployed (Dockerfile coming soon) and the app can be sent questions in the form: /bbc/question
### 4) A class called NLS parses and cleans the query and executes the appropriate query. The answer is then returned.
