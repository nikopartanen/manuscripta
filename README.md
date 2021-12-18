# Manuscripta

The original idea was to structure the code in this repository as a Python package. This is, however, still unfinished. The repository contains now three larger example scripts that address different work phases when working with text recognition materials, especially in the context of [Transkribus](https://transkribus.eu/). The main idea is to extract the data and manipulate it so that it can be further processed with different NLP libraries, such as [UralicNLP](https://github.com/mikahama/uralicnlp) and [murre](https://github.com/mikahama/murre).

## Functionality

### Editing Page XML files

Script `processing_page_xml.py` contains an example file used in Manuscripta Castreniana project to edit some of the proofread files. The same mechanism can be extended to different tasks. 

### Transkribus API

Script `transkribus_api.py` contains examples of how to use Transkribus API to investigate user collections and to retrieve documents. There is an example about saving all ground truth files into their own directory for further manipulation. 

### Editing Ground Truth data

Script `edit_ground_truth.py` contains examples of extracting the line polygons from Page XML, visualizing their locations with different parameters, and collecting individual lines into OCR model training experiments. The current structure 

### Transliteration

It is an extremely common issue that manuscripts or printed books contain texts in endangered languages in writing or transcription systems that are not widely used, possibly being used only in these documents. One convention our research group has used is transliteration, so that we apply rule based patterns into the original text, bringing it closer to current orthography. This works often very well when we operate on phonemic transcription systems in languages that have phonemic orthographies. Script `lat2cyr_kpv.py` illustrates this in Komi context.

