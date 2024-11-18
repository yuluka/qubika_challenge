import os
import json

import unstructured
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class RAG:
    """
    Retrieval Augmented Generation (RAG) model.

    This class is used to generate embeddings for a set of documents, retrieve relevant information based on a query, and augment the query with the relevant information.
    """

    def __init__(self, data_path: str = "data", chroma_path: str = "db", documents_type: str = "json", reload_db: bool = False):
        self.DATA_PATH: str = data_path
        self.CHROMA_PATH: str = chroma_path
        self.is_data: bool = False
        
        self.PROMPT_TEMPLATE: str = """
Answer the question based only on the context below:

{context}

-----------------------------------

Answer the question based on the above context: {question}
"""

        if not os.path.exists(self.CHROMA_PATH) or reload_db:
            if os.path.exists(self.DATA_PATH):
                documents: list[Document] = self.load_documents(documents_type)
                chunks: list[Document] = self.split_documents(documents)
                self.db: Chroma = self.generate_n_save_embeddings(chunks, reload_db)
            
        else:
            self.db: Chroma = self.generate_n_save_embeddings([], reload_db)


    def load_documents(self, documents_type: str) -> list[Document]:
        """	
        Load the documents from the data directory.

        :param documents_type: The type of documents to load.
        :type documents_type: str
        :return: The documents.
        :rtype: list[Document]
        """
        
        if documents_type == "json":
            documents: list[Document] = []

            for file in os.listdir(self.DATA_PATH):
                file_path = os.path.join(self.DATA_PATH, file)

                document_content = str(self.load_json_document(file_path))
                documents.append(Document(page_content=document_content))
            
            return documents

        loader: DirectoryLoader = DirectoryLoader(self.DATA_PATH, glob=f"*.{documents_type}")
        documents: list[Document] = loader.load()
        
        return documents


    def load_json_document(self, file_path: str) -> dict:
        """
        Load a JSON document from the given file path.

        :param file_path: The path to the JSON document.
        :type file_path: str
        :return: The JSON document.
        :rtype: dict
        """

        with open(file_path, "r", encoding="utf-8") as f:
            document = json.load(f)

        return document

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split the documents into chunks.

        :param documents: The documents to split.
        :type documents: list[Document]
        :return: The split documents.
        :rtype: list[Document]
        """

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )

        chunks = text_splitter.split_documents(documents)

        return chunks

    def generate_n_save_embeddings(self, chunks: list[Document], reload_db: bool) -> Chroma:
        """
        Generate and save the embeddings for the documents in a Chroma database.

        :param chunks: The documents to generate embeddings for.
        :type chunks: list[Document]
        :return: The Chroma database.
        :rtype: Chroma
        """

        if os.path.exists(self.CHROMA_PATH) and not reload_db:
            db: Chroma = Chroma(
                persist_directory=self.CHROMA_PATH,
                embedding_function=OpenAIEmbeddings(),
            )

            self.is_data = True

            return db

        db: Chroma = Chroma.from_documents(
            documents=chunks, 
            embedding=OpenAIEmbeddings(),
            persist_directory=self.CHROMA_PATH,
        )
        
        self.is_data = True

        return db

    def retrieve_relevant_info(self, db: Chroma, query: str, n: int = 3) -> list[Document]:
        """
        Retrieve relevant information based on a query.

        :param db: The Chroma database.
        :type db: Chroma
        :param query: The query to search for.
        :type query: str
        :param n: The number of results to return. Defaults to 3.
        :type n: int
        :return: The relevant information.
        :rtype: list[Document]
        """

        results: list[Document] = db.similarity_search(
            query=query,
            k=n,
        )

        if len(results) == 0:
            return []

        return results

    def augment_query(self, query: str) -> str:
        """
        Augment the query with relevant information.

        :param query: The query to augment.
        :type query: str
        :return: The augmented query.
        :rtype: str
        """

        if not self.is_data:
            return "No data available."

        relevant_info: list[Document] = self.retrieve_relevant_info(self.db, query)

        context: str = "\n\n---\n\n".join([doc.page_content for doc in relevant_info])
        prompt_template: ChatPromptTemplate = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)

        augmented_query: str = prompt_template.format(
            context=context,
            question=query,
        )

        return augmented_query
    
    def get_db(self):
        """
        Get the Chroma database.

        :return: The Chroma database.
        :rtype: Chroma
        """

        return self.db