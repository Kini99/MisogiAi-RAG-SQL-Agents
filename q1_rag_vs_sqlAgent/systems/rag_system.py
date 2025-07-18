"""
RAG (Retrieval-Augmented Generation) system implementation
"""
import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from systems.base_system import BaseQuerySystem, QueryResult
from config.database import SessionLocal
from config.settings import settings
from models.schema import Customer, Order, Product, Review, SupportTicket

class RAGSystem(BaseQuerySystem):
    """RAG system for natural language queries"""
    
    def __init__(self):
        super().__init__("RAG System")
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.llm = None
        self.documents = []
        
    def initialize(self) -> bool:
        """Initialize the RAG system"""
        try:
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
            
            # Initialize LLM
            if settings.OPENAI_API_KEY:
                self.llm = OpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model_name=settings.OPENAI_MODEL,
                    temperature=settings.OPENAI_TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
            else:
                # Fallback to a simple template-based approach
                self.llm = None
            
            # Create documents from database
            self._create_documents()
            
            # Create vector store
            self._create_vectorstore()
            
            # Create QA chain
            self._create_qa_chain()
            
            return True
        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            return False
    
    def _create_documents(self):
        """Create documents from database data"""
        db = SessionLocal()
        try:
            # Get all data from database
            customers = db.query(Customer).all()
            orders = db.query(Order).all()
            products = db.query(Product).all()
            reviews = db.query(Review).all()
            support_tickets = db.query(SupportTicket).all()
            
            # Create documents for each table
            for customer in customers:
                doc = self._customer_to_document(customer)
                self.documents.append(doc)
            
            for order in orders:
                doc = self._order_to_document(order, db)
                self.documents.append(doc)
            
            for product in products:
                doc = self._product_to_document(product)
                self.documents.append(doc)
            
            for review in reviews:
                doc = self._review_to_document(review, db)
                self.documents.append(doc)
            
            for ticket in support_tickets:
                doc = self._ticket_to_document(ticket, db)
                self.documents.append(doc)
                
        finally:
            db.close()
    
    def _customer_to_document(self, customer: Customer) -> Document:
        """Convert customer to document"""
        content = f"""
        Customer Information:
        ID: {customer.id}
        Name: {customer.first_name} {customer.last_name}
        Email: {customer.email}
        Phone: {customer.phone}
        Address: {customer.address}, {customer.city}, {customer.state}, {customer.country} {customer.postal_code}
        Created: {customer.created_at}
        Active: {customer.is_active}
        """
        return Document(
            page_content=content,
            metadata={
                "type": "customer",
                "customer_id": customer.id,
                "email": customer.email
            }
        )
    
    def _order_to_document(self, order: Order, db: Session) -> Document:
        """Convert order to document"""
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        content = f"""
        Order Information:
        Order ID: {order.id}
        Order Number: {order.order_number}
        Customer: {customer.first_name} {customer.last_name} ({customer.email})
        Status: {order.status}
        Total Amount: ${order.total_amount}
        Payment Status: {order.payment_status}
        Payment Method: {order.payment_method}
        Created: {order.created_at}
        """
        return Document(
            page_content=content,
            metadata={
                "type": "order",
                "order_id": order.id,
                "customer_id": order.customer_id,
                "status": order.status
            }
        )
    
    def _product_to_document(self, product: Product) -> Document:
        """Convert product to document"""
        content = f"""
        Product Information:
        ID: {product.id}
        Name: {product.name}
        Description: {product.description}
        Price: ${product.price}
        Category: {product.category}
        Brand: {product.brand}
        SKU: {product.sku}
        Stock: {product.stock_quantity}
        Active: {product.is_active}
        """
        return Document(
            page_content=content,
            metadata={
                "type": "product",
                "product_id": product.id,
                "category": product.category,
                "brand": product.brand
            }
        )
    
    def _review_to_document(self, review: Review, db: Session) -> Document:
        """Convert review to document"""
        customer = db.query(Customer).filter(Customer.id == review.customer_id).first()
        product = db.query(Product).filter(Product.id == review.product_id).first()
        content = f"""
        Review Information:
        ID: {review.id}
        Customer: {customer.first_name} {customer.last_name}
        Product: {product.name}
        Rating: {review.rating}/5
        Title: {review.title}
        Comment: {review.comment}
        Verified Purchase: {review.is_verified_purchase}
        Created: {review.created_at}
        """
        return Document(
            page_content=content,
            metadata={
                "type": "review",
                "review_id": review.id,
                "customer_id": review.customer_id,
                "product_id": review.product_id,
                "rating": review.rating
            }
        )
    
    def _ticket_to_document(self, ticket: SupportTicket, db: Session) -> Document:
        """Convert support ticket to document"""
        customer = db.query(Customer).filter(Customer.id == ticket.customer_id).first()
        content = f"""
        Support Ticket Information:
        ID: {ticket.id}
        Ticket Number: {ticket.ticket_number}
        Customer: {customer.first_name} {customer.last_name} ({customer.email})
        Subject: {ticket.subject}
        Description: {ticket.description}
        Priority: {ticket.priority}
        Status: {ticket.status}
        Category: {ticket.category}
        Assigned To: {ticket.assigned_to}
        Resolution: {ticket.resolution}
        Created: {ticket.created_at}
        """
        return Document(
            page_content=content,
            metadata={
                "type": "support_ticket",
                "ticket_id": ticket.id,
                "customer_id": ticket.customer_id,
                "status": ticket.status,
                "priority": ticket.priority,
                "category": ticket.category
            }
        )
    
    def _create_vectorstore(self):
        """Create vector store from documents"""
        if not self.documents:
            raise ValueError("No documents to create vector store")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        split_docs = text_splitter.split_documents(self.documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=settings.VECTOR_DB_PATH
        )
    
    def _create_qa_chain(self):
        """Create QA chain for answering questions"""
        if self.llm:
            # Use LLM-based QA chain
            prompt_template = """
            You are a helpful customer support assistant for an e-commerce company.
            Use the following context to answer the question at the end.
            
            Context: {context}
            
            Question: {question}
            
            Answer the question based on the context provided. If the information is not available in the context, say so.
            """
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                chain_type_kwargs={"prompt": prompt}
            )
        else:
            # Fallback to simple retrieval
            self.qa_chain = None
    
    def query(self, natural_language_query: str) -> QueryResult:
        """Execute a natural language query using RAG"""
        try:
            if self.qa_chain:
                # Use LLM-based QA chain
                response = self.qa_chain.run(natural_language_query)
                confidence_score = 0.8  # Placeholder
            else:
                # Simple retrieval-based approach
                docs = self.vectorstore.similarity_search(natural_language_query, k=3)
                response = self._format_retrieved_docs(docs)
                confidence_score = 0.6  # Placeholder
            
            # Get source documents
            source_docs = self.vectorstore.similarity_search(natural_language_query, k=3)
            source_texts = [doc.page_content[:200] + "..." for doc in source_docs]
            
            return QueryResult(
                query=natural_language_query,
                response=response,
                execution_time=0.0,  # Will be set by measure_performance
                memory_usage=0.0,    # Will be set by measure_performance
                confidence_score=confidence_score,
                source_documents=source_texts
            )
            
        except Exception as e:
            return QueryResult(
                query=natural_language_query,
                response="",
                execution_time=0.0,
                memory_usage=0.0,
                error=str(e)
            )
    
    def _format_retrieved_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents into a response"""
        if not docs:
            return "No relevant information found."
        
        response = "Based on the available information:\n\n"
        for i, doc in enumerate(docs, 1):
            response += f"{i}. {doc.page_content[:300]}...\n\n"
        
        return response
    
    def cleanup(self):
        """Clean up resources"""
        if self.vectorstore:
            self.vectorstore.persist()
        self.documents.clear() 