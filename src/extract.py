"""PDF에서 텍스트 / 표 / 이미지 요소를 추출하고 분류하는 함수 (수업 실습 ①)."""

from pathlib import Path

from unstructured.partition.pdf import partition_pdf


def extract_pdf_elements(path, fname, figures_dir):
    """
    PDF 파일에서 이미지, 테이블, 텍스트 블록을 추출합니다.

    path       : PDF가 있는 폴더 경로 (끝에 구분자 포함)
    fname      : PDF 파일 이름
    figures_dir: 추출된 이미지 파일이 저장될 폴더
    """
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    return partition_pdf(
        filename=path + fname,
        strategy="hi_res",                # 레이아웃 분석으로 표·이미지를 정밀 추출
        extract_images_in_pdf=True,       # 그림을 별도 파일로 저장
        infer_table_structure=True,       # 표의 행·열 구조를 추론
        chunking_strategy="by_title",     # 제목을 기준으로 텍스트 블록 분할
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=str(figures_dir),
    )


def categorize_elements(raw_pdf_elements):
    """
    PDF에서 추출한 요소들을 테이블과 텍스트로 분류합니다.

    raw_pdf_elements: unstructured.documents.elements 리스트
    """
    tables = []
    texts = []

    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            tables.append(str(element))       # 표는 tables 리스트
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            texts.append(str(element))        # 텍스트는 texts 리스트

    return texts, tables
