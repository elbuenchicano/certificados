import numpy as np
import os 
import argparse
import json
import subprocess 
import qrcode
import sys
import unidecode

##########################################################################
##########################################################################
def u_progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush() 


##########################################################################
##########################################################################
def make_qrcode(confs):
    vname_list  = confs ['names_file']
    out_dir     = confs ['out_dir']
    folio       = confs ['folio']


    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    #......................................................................
    out_file    = out_dir +'/list.txt'  
    f= open(out_file, "w+", encoding="latin-1" )
    for name_list, label in vname_list:

        out_file_list   = out_dir + '/' + label + '.json'
        folio = make_qrcode_single( confs, name_list, label, 
                                    out_dir, out_file_list, folio) 
        f.write(out_file_list+'#'+ label+'\n')
    
    f.close()

##########################################################################
##########################################################################
def make_qrcode_single(confs, name_list, label, out_dir, out_file_list, folio):
    ext         = confs ['ext']
    url         = confs ['url']
    
    out_path    = out_dir + '/qrimages/' 

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    #....................................................................
    file        = open(name_list, 'r') 
    vfiles      = []
    for line in file: 
        if len(line) > 0:
            vfiles.append(line)
    
    #....................................................................
    tam     = len(vfiles)
    ofiles  = {}
    for i in range(tam):
        
        line        = vfiles[i]
        if len(line) < 3:
            continue
        name, info  = line.split('#')
        name_o      = name.strip()
        name        = name_o.replace(' ', '_')
        name        = unidecode.unidecode(name)
        folio_id    = ( i + folio ) 
        imageid     = 'image' + str(folio_id)

        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_H,
            box_size = 10,
            border = 0,
        )
        
        qrcontent   = url + '/' + label + '__'+ name + '__'+ str(folio_id) +'.pdf'
        qr.add_data(qrcontent)
        qr.make(fit=True)

        img         = qr.make_image()
        out_name    = out_path + imageid + '.' + ext
        img.save(out_name)
        
        ofiles[name_o] =  {
                            "info"      : info.strip(), 
                            "name_"     : name, 
                            "qrlink"    : qrcontent, 
                            "id_folio"  : folio_id,
                            'qrimage'   : out_name
        }

        u_progress(i+1, tam, out_name) 

    #....................................................................
    out_file_list   = out_dir + '/' + label + '.json'

    with open(out_file_list, 'w+', encoding="latin-1") as fp:
        json.dump(ofiles, fp, ensure_ascii=False)

    return folio_id + 1

##########################################################################
##########################################################################
def generator(confs):
    
    out_dir         = confs ['out_dir']
    tokens          = confs ['tokens']   
    template_tex    = confs ['template']
    #logo           = confs ['logo']
    signature       = confs ['signature']

    #....................................................................
    out_path    = out_dir + '/texfiles/' 

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    #.....................................................................
    source_list = out_dir + '/list.txt' 
    file        = open(source_list, 'r') 
    vfiles      = []
    for line in file: 
        if len(line) > 0:
            vfiles.append( line.split('#') )

    #.....................................................................
    for file_list, label in vfiles:
        label       = label.strip()
        #loading file_list
        name_dict   = {}
        with open(file_list) as f:
            name_dict = json.load(f)

        template    = open(template_tex[label], 'r').read() 
        #template    = template.replace('$LOGO$', logo)
        template    = template.replace('$SIGNATURE$', signature)
        
        for token, value in tokens: 
            template = template.replace(token, value)
        #.................................................................
        if label == 'speaker':
            for item in name_dict: 
                name_       = name_dict[item]['name_']
                qrimage     = name_dict[item]['qrimage']
                info        = name_dict[item]['info']
                id_folio    = str(name_dict[item]['id_folio'])
                
                mail, title, rol = info.split('|') 

                content     = template.replace('$NAME$', item)
                content     = content.replace('$QR$', qrimage)
                content     = content.replace('$TITLE$', title)
                content     = content.replace('$NUMBER$', id_folio)
                content     = content.replace('$ROL$', rol)

                out_file    = out_path + label + '__'+ name_ + '__' + str(id_folio) + '.tex' 
                print('saving in: ', out_file)

                f= open(out_file, "w+", encoding="latin-1" )
                f.write(content)
                f.close()

                name_dict[item]['tex_file'] = out_file

        #.................................................................
        else:
            for item in name_dict: 
                name_       = name_dict[item]['name_']
                qrimage     = name_dict[item]['qrimage']
                id_folio    = str(name_dict[item]['id_folio'])

                content     = template.replace('$NAME$', item)
                content     = content.replace('$QR$', qrimage)
                content     = content.replace('$NUMBER$', id_folio)

                out_file    = out_path +  label + '__'+ name_ + '__' + id_folio +'.tex' 
                print('saving in: ', out_file)

                f= open(out_file, "w+", encoding="latin-1" )
                f.write(content)
                f.close()

                name_dict[item]['tex_file'] = out_file
            
        
        #..............................................
        #updating
        with open(file_list, 'w+', encoding="latin-1") as fp:
            json.dump(name_dict, fp, ensure_ascii=False)

##########################################################################
##########################################################################
def build_latex(confs):
    latex       = confs ['latex']
    ps          = confs ['ps']
    gs          = confs ['gs']
    #password    = confs ['pass']
    
    out_dir     = confs ['out_dir']
    event_name  = confs ['event_name']
    event_page  = confs ['event_page']
 
    out_path    = out_dir + '/pdf/' 

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    #....................................................................
    source_list = out_dir + '/list.txt' 
    file        = open(source_list, 'r') 
    vfiles      = []
    for line in file: 
        if len(line) > 0:
            vfiles.append( line.split('#') )

    #.....................................................................
    index_page_content = open('site.html', 'r').read()
    index_page_content = index_page_content.replace('$EVENT$', event_name)  
    index_page_content = index_page_content.replace('$SITE$', event_page)  

    content     = ''
    max_folio   = 0

    for file, label in vfiles:
        name_dict = {}
        with open(file) as f:
            name_dict = json.load(f)

        content = content + '<H2><B><I>'+ label + '</I></B></H2>\n'

        for item in name_dict: 
            os.system( latex + ' -output-directory '+ out_path + ' ' + name_dict[item]['tex_file'] ) 

            max_folio = max ( max_folio, name_dict[item]['id_folio'])  

            ps_out_name     = out_path + name_dict[item]['name_'] + '.ps'

            pdf_out_name    = os.path.basename(name_dict[item]['tex_file'])[:-3]

            pdf_out_name    = out_path + pdf_out_name + 'pdf'


            

            #os.system( gs + ' -dNOPAUSE -dBATCH -sDEVICE=ps2write -sOutputFile=' + ps_out_name + ' ' + pdf_out_name )

            #os.system( ps + ' ' + ps_out_name + ' ' + pdf_out_name)


            #descomentar las lineas de arriba


            #os.system( gs + ' -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dBATCH -dNOPROMPT -dNOPAUSE -dQUIET -sOwnerPassword=' + password + 
            #                ' -sUserPassword='  + password +
            #                ' -sOutputFile='    + pdf_out_name + ' ' + pdf_out_name)

            content = content + '<P><a href=' + name_dict[item]['qrlink'] + '>' + str(name_dict[item]['id_folio']) + '\t' + item  + '</a>'
    
    content = content + '<H1><B> Last Folio: '+ str(max_folio) + '</B></H1>\n'  

    index_page_content = index_page_content.replace('$CONTENT$', content)  

    out_file = out_path + '/list.html'     

    f= open(out_file, "w+", encoding="latin-1" )
    f.write(index_page_content)
    f.close()



##########################################################################
##########################################################################
def engine(confs):
    with open(confs) as f:
        data = json.load(f)
    
    functions = {   'generator'     : generator,
                    'build_latex'   : build_latex,
                    'make_qrcode'   : make_qrcode
    }

    vfunct   = data['funct']

    for funct in vfunct:
        confs   = {**data['general'], **data[funct]}
        functions[funct] (confs)
    

##########################################################################
##########################################################################
if __name__ == "__main__":
    parser  = argparse.ArgumentParser(description='')
    parser.add_argument('inputpath', nargs='?', 
                        help='The input path. Default = conf.json')
    args    = parser.parse_args()
    fil     = args.inputpath if args.inputpath is not None else './confs_spia2.json'

engine(fil)