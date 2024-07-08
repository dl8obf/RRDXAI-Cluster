# Wird für die Telnetverbindung benötigt
import telnetlib

# Wird für den Telnetserver benötigt, zusätzlich zu telnetlib
import socket

# Wird für das pattern matching benötigt
import re

# Wird für die Arrays benötigt
# import numpy as np


# Wird für die Records benötigt
from collections import namedtuple


# ========================================================================================================
# Definition von globalen Typen und Variablen:

# Definition eines records
Record = namedtuple('Record', ['time', 'spotter', 'dx_call', 'comment','relevance', 'attractiveness'])

# Ein Datum des oberen records wird mit Initialdaten befüllt:
r = Record(time='2021-11-01 13:45:00', spotter='DL2ABC', dx_call='K3LR', comment='This is a test.', relevance=8, attractiveness=9)

# Es wird eine Datei für die Clusterspots erzeugt, an diese soll "angehängt" (append) werden
clusterspots = open('clusterspots.txt','a')

# Define regular expressions
# original: callsign_pattern = "([a-z|0-9|'-'|'#'/]+)"
callsign_pattern = "(...[a-z0-9#/-]+)"
# Das callsign_pattern hat noch Probleme mit dem _# am Ende der CW-Skimmermeldungen. Patternmatching muss erweitert werden, damit die Skimmerspots richtig angezeigt werden.
frequency_pattern = "([0-9|.]+)"
pattern = re.compile("^DX de "+callsign_pattern+":\s+"+frequency_pattern+"\s+"+callsign_pattern+"\s+(.*)\s+(\d{4}Z)", re.IGNORECASE)

# Definition der verwendeten Clusterliste:
cluster_list = [
 
    ["Suederbrarup", "db0sue.de", 8000,"DL8OBF"],
    ["RRDXAI", "logbook.rrdxa.org", 8000,"DL8OBF"],
    ["SP2PUT_Skimmer", "klub.sp2put.pl", 7300,"DL8OBF"],
    ["Localskim", "localhost",7300,"DL8OBF"]
 
]
print("Clusterliste ist eingelesen.")


# Aufsetzen des Output-Telnetservers (antwortet auf Port 23)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 23))
server_socket.listen(1)

print('Ausgangs-Telnetserver hört auf Localhost, port 23...')

client_socket, addr = server_socket.accept()
print('Connection from:', addr)

client = telnetlib.Telnet()
client.sock = client_socket

client.write(b'Welcome to the RRDXAI local Telnet server!\r')
client.write(b'Enter "exit" to disconnect.\r')


# Das Folgende sind die verwendeten Cluster in der Form: Name, URL, Port, verwendeter Username
# Eine Passwortabfrage wird vorerst nicht unterstützt 


# Jetzt wird in alle Cluster aus der Clusterliste nacheinander eingeloggt
for cluster in cluster_list:
 
     # Verbinde zum Telnet-Cluster

     print("Verbindung zu ", cluster[0],"  ",cluster[1]," port: ", cluster[2])
     match cluster[0]:
          case "Suederbrarup":
                tn = telnetlib.Telnet(cluster[1],8000)
                

                # Erhalte die Login-Bestätigung des Clusters
                login = tn.read_until(b"login:")

                # Sende den Benutzername
                tn.write(b"DL8OBF\n")
                print("Benutzername DL8OBF an",cluster[0]," gesendet. ")
 
    
          case "RRDXAI":
               tn1 = telnetlib.Telnet(cluster[1],8000)

               # Erhalte die Login-Bestätigung des Clusters
               login = tn1.read_until(b"login:")
     
 
    
               # Sende den Benutzername
               tn1.write(b"DL8OBF\n")
               print("Benutzername DL8OBF an",cluster[1]," gesendet. ")

               # Fragt alle Meldungen des Clusters ab, bis wieder ein Prompt kommt
               login = tn1.read_until(b">")

          case "SP2PUT_Skimmer":
               tn2 = telnetlib.Telnet(cluster[1],7300)

               # Erhalte die Login-Bestätigung des Clusters
               login = tn2.read_until(b"login:")
               tn2.write(b"DL8OBF\n")
               print("Benutzername DL8OBF an",cluster[1]," gesendet. ")

               # Fragt alle Meldungen des Clusters ab, bis wieder ein Prompt kommt
               login = tn2.read_until(b"dxspider >")

               
          case "Localskim": 
               # Der lokale Skimmer meldet normalerweise:
               # Welcome to the CW Skimmer Telnet cluster port!
               # CW Skimmer 2.1 is operated by Uwe, DL8OBF in Hohenhameln (JO52AG)
               # Please enter your callsign:
               # DL8OBF de SKIMMER 2024-07-06 10:40Z CwSkimmer >
               
               tn3 = telnetlib.Telnet(cluster[1],7300)

               # Erhalte die Login-Bestätigung des Clusters
               login = tn3.read_until(b")")

 
    
               # Sende den Benutzername
               tn3.write(b"DL8OBF\n")
               print("Benutzername DL8OBF an:",cluster[0]," gesendet. ")
 
     # Wir gehen vorerst von Clustern ohne Passwort aus, deshalb der folgende Block auskommentiert
     # Erhalte die Passwortanforderung des Clusters
 
     # password = tn.read_until(b"Password:")
 
    
 
     # Sende das Passwort
 
     # tn.write(b"RRDXA4ever\n")
 


while(1):
# Abfrage von Cluster1:

          # Check new telnet info against regular expression 
          telnet_output = str(tn.read_until(b"\n", timeout = 2), encoding='UTF-8')
          print("TN: ",telnet_output)

          match = pattern.match(telnet_output)
          

         # clusterspots.write("TN: ")
   
          # If there is a match, sort matches into variables and write text into file

          if match:
               r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=9)
               client.write(r)
               if len(r.dx_call)>6:
                    print("Aufwertung aufgrund Länge de DX_Calls")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=100)
                    
                    
               if len(r.dx_call) <4:
                    print("Aufwertung aufgrund Kürze des DX_Calls")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=100)
                      
               if len(r.dx_call) <2:
                    print("Relevanz von zweistelligen Rufzeichen ist gering.")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=2, attractiveness=9)
                      
                      
               clusterspots.write(telnet_output)
                 
          # Check new telnet info against regular expression
          telnet_output = str(tn1.read_until(b"\n", timeout = 6), encoding='UTF-8')
          print("TN1: ",telnet_output)
          match = pattern.match(telnet_output)
   
          # If there is a match, sort matches into variables

          if match:
               r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=9)
               if len(r.dx_call)>6:
                    print("Aufwertung aufgrund Länge de DX_Calls")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=100)
                    
                    
               if len(r.dx_call) <4:
                    print("Aufwertung aufgrund Kürze des DX_Calls")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=100)
                      
               if len(r.dx_call) <2:
                    print("Relevanz von zweistelligen Rufzeichen ist gering.")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=2, attractiveness=9)

               # print (r)
               # clusterspots.write(telnet_output)


               # Dies sorgt dafür, dass tatsächslich jetzt in die Datei geschrieben wird
               clusterspots.close
               clusterspots = open('clusterspots.txt','a')
               

          # Check new telnet info against regular expression
          telnet_output = str(tn2.read_until(b"\n", timeout = 2), encoding='UTF-8')
          print("TN2: ",telnet_output)
          match = pattern.match(telnet_output)
         # clusterspots.write("TN: ")
   
          # If there is a match, sort matches into variables and write text into file

          if match:
               r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=9)
               if len(r.dx_call)>6:
                    print("Aufwertung aufgrund Länge de DX_Calls")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=100)
                    
                    
               if len(r.dx_call) <4:
                    print("Aufwertung aufgrund Kürze des DX_Calls")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=8, attractiveness=100)
                      
               if len(r.dx_call) <2:
                    print("Relevanz von zweistelligen Rufzeichen ist gering.")
                    r = Record(time=match.group(5), spotter=match.group(1), dx_call=match.group(3), comment=match.group(4).strip(), relevance=2, attractiveness=9)
                      
               clusterspots.write(telnet_output)
 
# Schließe die Telnet-Verbindung, hier kommt das Programm nur her, wenn nur eine zusätzliche Escaperoutine für das o.g. "while(1)" geschaffen wird
 
tn.close()
client.close() 
    
 
