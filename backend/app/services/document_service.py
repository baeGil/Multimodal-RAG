from unstructured.partition.pdf import partition_pdf
import shutil, os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Extract elements from PDF
def extract_texts_and_images(path, fname):
    """
    Extract images and chunk text from a PDF file.
    path: File path, which is used to dump images (.jpg)
    fname: File name
    """
    return partition_pdf(
        filename=path +"/"+ fname,
        extract_images_in_pdf=True,
        extract_image_block_types=["Image"],
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        extract_image_block_output_dir=path,
    )

# extract tables from pdf
def extract_tables(path, fname):
    return partition_pdf(
        filename=path +"/"+ fname,
        infer_table_structure=True,
        strategy='hi_res',
    )
    
# Categorize elements by type
def categorize_elements(element, type):
    """
    Categorize extracted elements from a PDF into tables and texts.
    element: List of unstructured.documents.elements
    """
    unstructured_element = [el for el in element if el.category == type]
    result = [el.text for el in unstructured_element]
    return result

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