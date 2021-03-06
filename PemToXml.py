#!/usr/bin/env python
#
# Converting RSA PEM key (PKCS#1) to XML compatible for .Net
# from https://github.com/MisterDaneel/
# extended with Python 3 support https://github.com/Alex-ley/PemToXml
#
# Need pycrypto installed.
#
from Crypto.Util import number
from Crypto.Util.asn1 import DerSequence
from Crypto.PublicKey import RSA
from base64 import standard_b64encode, b64decode
from binascii import a2b_base64
from os.path import basename, exists
from xml.dom import minidom
# import lxml.etree as et # alternative xml lib
import argparse
#
# CreateXMLPubKey
#
def pubKeyXML(pemPublicKeyFile):
   with open (pemPublicKeyFile, 'rb') as pkFile:
      pemPublicKey = pkFile.read()
   publicKey = RSA.importKey(pemPublicKey)

   doc = minidom.Document()
   root = doc.createElement('RSAKeyValue')
   doc.appendChild(root)

   xml_tag_list = ['Modulus', 'Exponent']
   public_key_attrs = ['n', 'e']

   for tag, attr in zip(xml_tag_list, public_key_attrs):
       elem = doc.createElement(tag)
       textNode = doc.createTextNode(standard_b64encode(number.long_to_bytes(getattr(publicKey, attr))).decode("utf-8"))
       elem.appendChild(textNode)
       root.appendChild(elem)

   fileName = basename(pemPublicKeyFile)
   with open (fileName+'.xml', 'w') as pkFile:
      pkFile.write(doc.toprettyxml())
   return
#
# CreateXMLPrivKey
#
def privKeyXML(pemPrivateKeyFile):
   with open (pemPrivateKeyFile, 'rb') as pkFile:
      pemPrivKey = pkFile.read()
   # print(pemPrivKey)
   lines = pemPrivKey.replace(" ".encode('utf-8'), ''.encode('utf-8')).split()
   # print(lines)
   lines_str = [x.decode("utf-8") for x in lines]
   keyDer = DerSequence()
   keyDer.decode(a2b_base64(''.join(lines_str[1:-1])))

   doc = minidom.Document()
   root = doc.createElement('RSAKeyValue')
   doc.appendChild(root)

   xml_tag_list = ['Modulus', 'Exponent', 'D', 'P', 'Q', 'DP', 'DQ', 'InverseQ']

   for idx, tag in enumerate(xml_tag_list, start=1):
       elem = doc.createElement(tag)
       textNode = doc.createTextNode(standard_b64encode(number.long_to_bytes(keyDer[idx])).decode("utf-8"))
       elem.appendChild(textNode)
       root.appendChild(elem)

   fileName = basename(pemPrivateKeyFile)
   with open (fileName+'.xml', 'w') as pkFile:
      pkFile.write(doc.toprettyxml())
   return
#
# Get Long Int
#
def GetLong(nodelist):
   rc = []
   for node in nodelist:
      if node.nodeType == node.TEXT_NODE:
         rc.append(node.data)
   string = ''.join(rc)
   return number.bytes_to_long(b64decode(string))
#
# CreatePEMPubKey
#
def pubKeyPEM(xmlPublicKeyFile):
   with open (xmlPublicKeyFile, 'rb') as pkFile:
      xmlPublicKey = pkFile.read()
   rsaKeyValue = minidom.parseString(xmlPublicKey)
   modulus = GetLong(rsaKeyValue.getElementsByTagName('Modulus')[0].childNodes)
   exponent = GetLong(rsaKeyValue.getElementsByTagName('Exponent')[0].childNodes)
   publicKey = RSA.construct((modulus, exponent))
   fileName = basename(xmlPublicKeyFile)
   with open (fileName+'.pem', 'w') as pkFile:
      pkFile.write(publicKey.exportKey().decode('utf-8'))
   return
#
# CreatePEMPrivKey
#
def privKeyPEM(xmlPrivateKeyFile):
   with open (xmlPrivateKeyFile, 'rb') as pkFile:
      xmlPrivateKey = pkFile.read()
   rsaKeyValue = minidom.parseString(xmlPrivateKey)
   modulus = GetLong(rsaKeyValue.getElementsByTagName('Modulus')[0].childNodes)
   exponent = GetLong(rsaKeyValue.getElementsByTagName('Exponent')[0].childNodes)
   d = GetLong(rsaKeyValue.getElementsByTagName('D')[0].childNodes)
   p = GetLong(rsaKeyValue.getElementsByTagName('P')[0].childNodes)
   q = GetLong(rsaKeyValue.getElementsByTagName('Q')[0].childNodes)
   qInv = GetLong(rsaKeyValue.getElementsByTagName('InverseQ')[0].childNodes)
   privateKey = RSA.construct((modulus, exponent, d, p, q, qInv))
   fileName = basename(xmlPrivateKeyFile)
   with open (fileName+'.pem', 'w') as pkFile:
      pkFile.write(privateKey.exportKey().decode('utf-8'))
   return
#
# Parser args
#
def parse_args():
   """Create the arguments"""
   parser = argparse.ArgumentParser('\nPemToXml.py --xmltopem --public mypublickeyfile.xml\nPemToXml.py --pemtoxml --private myprivatekeyfile.pem')
   parser.add_argument("-pub", "--public", help="Public Key")
   parser.add_argument("-priv", "--private", help="Private Key")
   parser.add_argument("-xtop", "--xmltopem", help="XML to PEM", action='store_true')
   parser.add_argument("-ptox", "--pemtoxml", help="PEM to XML", action='store_true')
   return parser.parse_args()
#
# Main
#
def main(args):
   if args.pemtoxml:
      if args.public:
         inputfile = args.public
         pubKeyXML(inputfile)
      elif args.private:
         inputfile = args.private
         privKeyXML(inputfile)
   elif args.xmltopem:
      if args.public:
         inputfile = args.public
         pubKeyPEM(inputfile)
      elif args.private:
         inputfile = args.private
         privKeyPEM(inputfile)
   else:
      print('Nothing to do')
if __name__ == "__main__":
   main(parse_args())
