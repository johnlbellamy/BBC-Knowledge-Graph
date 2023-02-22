import nltk
from py2neo import Graph
import pandas as pd
from pprint import pprint
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy
from spacy import displacy
import en_core_web_sm
from nltk import pos_tag
from itertools import groupby
import pickle


class NLS:

    def __init__(self, question):

        self.question = question
        self.companies = pickle.load(open('nls-app/companies.p', 'rb'))
        self.companies_map = pickle.load(open('nls-app/companies_map.p', 'rb'))


    def connect():
        global graph
        graph = Graph("bolt://localhost:7687", auth = ("neo4j", "test"))
        tx = graph.begin()
    
    def tokenize(self):
    
        question_tokenized = word_tokenize(self.question)
        
        stop_words = set(stopwords.words('english'))
        
        filtered_question = [w for w in question_tokenized if not w in stop_words]
        
        filtered_question = []
    
        for w in question_tokenized:
        
            if w not in stop_words:
            
                filtered_question.append(w)
            
        self.filtered_question = filtered_question

    def tag(self):
    
        ner, tags = [], []
        
        nlp = en_core_web_sm.load()
        
        doc = nlp(self.question)
        
        ner = [(X.text, X.label_) for X in doc.ents]
            
        #displacy.render(doc)
        
        tags = pos_tag(self.filtered_question)
        
        groups = groupby(tags, key=lambda x: x[1])
        
        names_tagged = [[w for w,_ in words] for tag,words in groups if tag=="NNP"]
        
        names = [" ".join(name) for name in names_tagged if len(name)>=2]
        
        if len(ner) == 0:
            
            if any([x in self.companies for x in self.filtered_question]):
                
                matches = [x for x in self.companies if x in self.filtered_question]
                
                for m in matches:
                    
                    ner.append((m, "ORG"))
                
        self.ner = ner
        self.tags = tags 

    def params_builder(self):
    
        params, params_2 = {}, {}
        
        if len(self.ner) == 1:
            
            if (self.ner[0][1] == 'GPE') or (self.ner[0][1] == 'LOC'):
                
                if (self.ner[0][0] == "US") or (self.ner[0][0] == "USA"):
                    
                    country_ = 'United States'
                    
                elif (self.ner[0][0] == "UK"):
                    
                    country_ = 'United Kingdom'
                    
                else:
                    
                    country = self.ner[0][0]
                    
                    params = {}
                    
                    params["country"] = country
                    
            elif (self.ner[0][1] == 'ORG'):
                
                org = self.ner[0][0]
                
                params = {}
                
                try:

                    params["org"] = self.companies_map[org]

                except:

                    params["org"] = org
                
            elif (self.ner[0][1] == 'PERSON'):
                
                person = self.ner[0][0]
                
                params = {}
                
                params["person"] = person
                
        elif len(self.ner) > 1:
            
            name1 = self.ner[0][0]
            
            name2 = self.ner[1][0]
            
            params_2 = {"name1":name1, "name2":name2}
            
        self.params = params 
        self.params_2 = params_2

    def query_picker(self):
    
        label_p = "(p:Person)"
        label_o = "(o:Company)"
        label_l = "(l:NE_Location)"
        works = "-[r:WORKS_FOR]-"
        lives = "-[:LIVES_IN]-"

        query1 = '''
        match {} {} {}
        where p.value IN $person
        return p.value as Name,r.value as Works_as,o.value as at
        '''.format(label_p,works,label_o)

        query1_1 = '''
        match {} {} {}
        where o.value IN $org
        return o.value as Organization, collect(distinct p.value) as Person, r.value as Position
        '''.format(label_p,works,label_o)

        query2 = '''
        match (p:Person {value:$person})-[r:LIVES_IN]-(l:Location)
        return p.value as Person, l.value as STAYS_AT
        '''

        query3 = '''
        MATCH (p1:NER_Person:Tag{ value: $name1 }),(p2:NER_Person:Tag{ value: $name2 }), p = shortestPath((p1)-[*..15]-(p2))
        RETURN p1.value as Person1, p2.value as Person2, p as Relation
        '''

        query4 = '''
        MATCH (p:NER_Person)-[w:LIVES_IN]->(o:NER_Location)
        RETURN p.value as Person ,o.value as Lives_in
        '''.format(label_p,lives,label_o)

        query5 = '''
        MATCH (p:NER_Person)-[:LIVES_IN]->(l:NER_Location), (p)-[w:WORKS_AT]-(o:NER_Organization)
        RETURN p.value as Person, l.value as Lives_in, o.value as Works_at, w.AS as Position
        '''

        query6 = '''
        MATCH (s:Sentence)-[st:SENTENCE_TAG_OCCURRENCE]->(n:TagOccurrence), (s)-[h:HAS_TAG]-(p:NER_Person), (s)-[h]-(o:NER_Organization)
        where n.value IN ["said","says","think","thinks"] AND (p.value in $names OR o.value in $org)
        return s.text as Sentence, p.value as Person
        '''

        query7 = '''
        match (a:Article)-[:HAS_ANNOTATED_TEXT]-(at:AnnotatedText)-[:CONTAINS_SENTENCE]-(s:Sentence)-[:SENTENCE_TAG_OCCURRENCE]-(t:TagOccurrence)-[:TAG_OCCURRENCE_TAG]-(o:NER_Organization)
        where o.value = $org
        return distinct a.Text

        '''

        query8 = '''
        match (a:Article)-[:HAS_ANNOTATED_TEXT]-(at:AnnotatedText)-[:CONTAINS_SENTENCE]-(s:Sentence)-[:SENTENCE_TAG_OCCURRENCE]-(t:TagOccurrence)-[:TAG_OCCURRENCE_TAG]-(p:NER_Person)
        where p.value = $person
        return distinct a.Text

        '''

        for word,tag in self.tags:

            if word in ['work','do']:

                self.response = [graph.run(query1, self.question, self.params).data(), "rdf-triple"]

            elif word in ['works','at']:

                self.response = [graph.run(query1_1, self.params).data(), "rdf-triple"]

            elif word in ['live','reside','stay', 'live?']:

                self.response = [graph.run(query2, self.params).data(), "rdf-triple"]

            elif word in ['related','relation']:

                self.response = graph.run(query3, self.params_2).data()

            elif word in ['live','lives']:

                self.response = [graph.run(query4).data(), "rdf-triple"]

            elif word in ['everyone']:

                self.response = graph.run(query5).data()

            elif word in ['think', 'says', 'say']:

                self.response = graph.run(query6, self.params).data() 

            elif word in ['article','articles', 'Article','Articles']:

                if self.params.get('org'):

                    self.response = [graph.run(query7, self.params).data(), "article"]

                else:
                    
                    words = [x[0] for x in self.tags if x[1] == "NNP"] 

                    params = {"person":" ".join(words)}
                    self.response = [graph.run(query8, params).data(), "article"]
                    
            elif 'person' in self.params:
                
                self.response = [graph.run(query8, self.params).data(), "article"]
                
            elif 'org' in self.params:
                
                self.response = [graph.run(query7, self.params).data(), "article"]
                
