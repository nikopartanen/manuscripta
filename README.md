# Manuscripta

This is a Python package that contains various functions to process and evaluate text recognition materials. It supports currently Page XML and Alto XML formats. The package is intended to be used in connection with other Python packages that offer higher level functionality, such as [UralicNLP](https://github.com/mikahama/uralicnlp) and [murre](https://github.com/mikahama/murre).

## Functionality

### Reading OCR XML files

Function `read_ocr_xml()` can be used to read two commonly used XML types with returned list of dictionaries.

### Visualization

Function `plot_page()` takes arguments `xml_file` an `image_file`, and returns an image with the layout elements highlighted.

### Transliteration

It is extremely common that transcribed materials are in very rare writing systems. The package contains few transliteration patterns that have been useful in our work.
