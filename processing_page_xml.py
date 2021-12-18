from pathlib import Path
import xml.etree.cElementTree as ET
import re

# At times it is useful to pick out the values
# about offsets. For example, we may want to know
# where superscript and subscripts are tagged.

def get_offset_info(offsets):
    
    offset_dicts = []
    
    for offset in offsets:
        
        info = {}
        
        info['type'] = re.findall('((super|sub)script)', offset)[0][0]
        info['start'] = int(re.findall('(?<=offset:)\d+', offset)[0])
        info['length'] = int(re.findall('(?<=length:)\d+', offset)[0])
        
        offset_dicts.append(info)

    for position, offset in enumerate(offset_dicts):
                
        if position == 0:
            
            offset['scriptlength'] = offset['length'] + 2
        
        if position != 0:
            
            offset['start'] = offset['start'] + (2 * position)
            offset['scriptlength'] = offset['length'] + 2
                
    return offset_dicts

# One common convention when training the model to detect
# subscript and superscript is to mark subscript with // and 
# superscript with \\. 
def return_marked_string(string, offsets):

    offset_info = get_offset_info(offsets)

    for offset in offset_info:

        if offset['type'] == 'subscript':

            marker = '/'

        if offset['type'] == 'superscript':

            marker = '\\'

        start = offset['start']
        length = offset['length']

        string = string[:start] + marker + string[start:start + length] + marker + string[start + length:]
    
    offset_strings = []
    
    for offset in offset_info:
        
        offset_string = f"textStyle {{offset:{offset['start']}; length:{offset['scriptlength']};{offset['type']}:true;}}"
        offset_strings.append(offset_string)

    fixed_string = ' '.join(offset_strings)
        
    return string, fixed_string

# This is an example of manipulating the Page XML with the
# functions above. We remove the word level items, Transkribus
# seems to generate those when documents are imported, and this way 
# we have no danger of having different versions in different parts of
# the document
def convert_subscript_to_text(page_xml, target_file):

    tree = ET.parse(page_xml)
    root = tree.getroot()

    xmlns = {'page': '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}'}

    for line in root.findall('.//{page}TextLine'.format(**xmlns)):

        for word in line.findall('.//{page}Word'.format(**xmlns)):

            line.remove(word)

    for line in root.findall('.//{page}TextLine'.format(**xmlns)):

        custom = line.get('custom')

        if 'superscript' in custom or 'subscript' in custom:

            styles = re.findall('textStyle ({.+?})', custom)

            textnode = line.find('.//{page}TextEquiv/{page}Unicode'.format(**xmlns))

            new_string, new_style = return_marked_string(textnode.text, styles)

            new_custom = re.sub(r'textStyle.+', new_style, custom)

            line.set('custom', new_custom)

            textnode.text = new_string

    ET.register_namespace('',"http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15")

    tree.write(target_file,
               xml_declaration=True, 
               encoding='utf-8',
               method="xml")

# Example call
# convert_subscript_to_text(page_xml = './386199/Worterbuch_1937/page/Worterbuch_1937-004_2R.xml',
#                         target_file = 'test/Worterbuch_1937-004_2R.xml')