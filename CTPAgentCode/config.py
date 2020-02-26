import os
from xml.etree import ElementTree as et
def config():
    SVN_username=''
    SVN_password=''
    SVN_path=''
    nmap_path=''
    config = open("config.xml").read()
    root = et.fromstring(config)
    for child_of_root in root:
        if child_of_root.tag == 'messages':
            for child_of_root2 in child_of_root:
                if child_of_root2.tag == 'message':
                    SVN_username = child_of_root2.get('SVN_username')
                    SVN_password = child_of_root2.get('SVN_password')
        if child_of_root.tag == 'directions':
            for child_of_root2 in child_of_root:
                if child_of_root2.tag == 'direction':
                    SVN_path = child_of_root2.get('SVN_path')
                    nmap_path = child_of_root2.get('nmap_path')
                # print(child_of_root2.tag, child_of_root2.attrib)
    return SVN_username,SVN_password,SVN_path,nmap_path

if __name__ == '__main__':
    re=config()

    print("root是",re)