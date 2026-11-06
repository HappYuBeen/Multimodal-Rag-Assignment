"""다중 벡터 검색기: 요약으로 검색하고, 같은 doc_id로 연결된 원본을 돌려줍니다 (수업 실습 ③)."""

import re
import uuid

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

# langchain 1.x 와 0.3 에서 클래스 위치가 달라 두 경로를 모두 시도합니다.
try:
    from langchain_classic.retrievers.multi_vector import MultiVectorRetriever
except ImportError:
    from langchain.retrievers.multi_vector import MultiVectorRetriever

try:
    from langchain_core.stores import InMemoryStore
except ImportError:
    from langchain.storage import InMemoryStore


def build_retriever(collection_name="multimodal_rag", id_key="doc_id"):
    """요약은 vectorstore(색인 카드 서랍), 원본은 docstore(서가)에 두는 검색기를 만듭니다."""
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    )
    store = InMemoryStore()

    return MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )


def add_documents(retriever, doc_summaries, doc_contents):
    """요약본은 벡터 DB에, 원본은 docstore에 '같은 id'로 저장합니다."""
    id_key = retriever.id_key
    doc_ids = [str(uuid.uuid4()) for _ in doc_contents]

    summary_docs = [
        Document(page_content=s, metadata={id_key: doc_ids[i]})
        for i, s in enumerate(doc_summaries)
    ]

    retriever.vectorstore.add_documents(summary_docs)               # 요약본 -> vectorstore
    retriever.docstore.mset(list(zip(doc_ids, doc_contents)))       # 원본 -> docstore


def split_image_text_types(docs):
    """검색 결과를 Base64 이미지와 텍스트로 나눕니다."""
    b64_images = []
    texts_out = []

    for doc in docs:
        content = doc.page_content if isinstance(doc, Document) else doc

        # Base64 문자열은 영문/숫자/+/= 만으로 길게 이어집니다
        if re.match("^[A-Za-z0-9+/]{100,}={0,2}$", content):
            b64_images.append(content)
        else:
            texts_out.append(content)

    return {"images": b64_images, "texts": texts_out}
