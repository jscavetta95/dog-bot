from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, or_, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Node(Base):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True)
    label = Column(String)

    subject_triple = association_proxy('subject_triple', 'subject')
    object_triple = association_proxy('object_triple', 'object')

    def __repr__(self):
        return self.label


class Triple(Base):
    __tablename__ = 'triple'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('node.id'), nullable=False)
    predicate = Column(String, nullable=False)
    object_id = Column(Integer, ForeignKey('node.id'), nullable=True)

    UniqueConstraint('subject_id', 'predicate', 'object_id')

    subject = relationship(Node, primaryjoin=(subject_id == Node.id), backref="subject_triple")
    object = relationship(Node, primaryjoin=(object_id == Node.id), backref="object_triple")

    def __repr__(self):
        if self.object:
            return f'{self.subject} {self.predicate} {self.object}'
        else:
            return f'{self.subject} {self.predicate}'


class KnowledgeBase:

    def __init__(self, database_name, nlp):
        self.session = self.__load_database(database_name)
        self.nlp = nlp

    def add_triple(self, subject_label, predicate, object_label=None):
        subject_node = self.__create_node(self.__normalize(subject_label))
        if object_label:
            object_node = self.__create_node(self.__normalize(object_label))
            self.__create_triple(subject_node.id, self.__normalize(predicate), object_node.id)
        else:
            self.__create_triple(subject_node.id, self.__normalize(predicate))

        self.session.commit()

    def __create_node(self, node_label):
        node = self.session.query(Node).filter_by(label=node_label).first()
        if node is None:
            node = Node(label=node_label)
            self.session.add(node)
            self.session.flush()
        return node

    def __create_triple(self, subject_id, predicate, object_id=None):
        if not self.__triple_exists(subject_id, predicate, object_id):
            triple = Triple(subject_id=subject_id, object_id=object_id, predicate=predicate)
            self.session.add(triple)
            self.session.flush()

    def retrieve_triples(self, node_label):
        node_id = self.session.query(Node.id).filter_by(label=self.__normalize(node_label)).scalar()
        if node_id is None:
            return False
        else:
            triples = self.session.query(Triple).filter(or_(Triple.subject_id == node_id,
                                                            Triple.object_id == node_id)).all()
            return triples

    def find_triple(self, subject_label, predicate, object_label=None):
        subject_id = self.session.query(Node.id).filter_by(label=self.__normalize(subject_label)).scalar()
        if object_label:
            object_id = self.session.query(Node.id).filter_by(label=self.__normalize(object_label)).scalar()
            if object_id:
                return self.__triple_exists(subject_id, self.__normalize(predicate), object_id)
            else:
                return False
        else:
            return self.__triple_exists(subject_id, self.__normalize(predicate))

    def __triple_exists(self, subject_id, predicate, object_id=None):
        if object_id:
            triple = self.session.query(Triple).filter_by(subject_id=subject_id, predicate=predicate,
                                                          object_id=object_id).first()
        else:
            triple = self.session.query(Triple).filter_by(subject_id=subject_id, predicate=predicate).first()

        if triple is None:
            return False
        else:
            return True

    @staticmethod
    def __normalize(token):
        return token.lemma_

    @staticmethod
    def __load_database(database_name):
        engine = create_engine(f'sqlite:///{database_name}')
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        return session
