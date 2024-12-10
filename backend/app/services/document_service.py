from unstructured.partition.pdf import partition_pdf
import shutil, os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Extract elements from PDF using unstructured
def extract_pdf_elements(path, fname):
    """
    Extract images, tables, and chunk text from a PDF file.
    path: File path, which is used to dump images (.jpg)
    fname: File name
    """
    return partition_pdf(
        filename=path +"/"+ fname,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        extract_image_block_output_dir=path,
    )

# Categorize elements by type
def categorize_elements(raw_pdf_elements):
    """
    Categorize extracted elements from a PDF into tables and texts.
    raw_pdf_elements: List of unstructured.documents.elements
    """
    tables = []
    texts = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            tables.append(str(element))
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            texts.append(str(element))
    return texts, tables

# Relocate images and tables

def relocate(fpath,fname):
    # Đường dẫn tới file PDF
    pdf_path = fpath+"/"+fname
    pdf_dir = os.path.dirname(pdf_path)

    # Đường dẫn tới các thư mục đích
    table_output_dir = os.path.join(pdf_dir, "tables")
    image_output_dir = os.path.join(pdf_dir, "images")

    # Tạo các thư mục nếu chưa tồn tại
    os.makedirs(table_output_dir, exist_ok=True)
    os.makedirs(image_output_dir, exist_ok=True)

    # Liệt kê các tệp trong thư mục của file PDF
    for filename in os.listdir(pdf_dir):
        # Đường dẫn đầy đủ tới từng file
        file_path = os.path.join(pdf_dir, filename)
    
        # Kiểm tra nếu là file bảng và di chuyển vào thư mục tables
        if filename.startswith("table-") and filename.endswith(".jpg"):
            shutil.move(file_path, os.path.join(table_output_dir, filename))
    
        # Kiểm tra nếu là file hình ảnh và di chuyển vào thư mục images
        elif filename.startswith("figure-") and filename.endswith(".jpg"):
            shutil.move(file_path, os.path.join(image_output_dir, filename))
    return table_output_dir, image_output_dir