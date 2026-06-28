import opendataloader_pdf
import os


def discover_pdfs():
    list_of_pdfs = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pdf"):
                list_of_pdfs.append(os.path.join(root, file))
    return list_of_pdfs


def main():

    list_of_pdfs = discover_pdfs()
    # Batch all files in one call — each convert() spawns a JVM process, so repeated calls are slow
    opendataloader_pdf.convert(
        input_path=list_of_pdfs,
        output_dir="output/",
        format="markdown,json",
        image_format="png",  # "png" or "jpeg"
        # use_struct_tree=True,  # Use native PDF structure
    )


if __name__ == "__main__":
    main()
