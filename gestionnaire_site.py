#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================[  DETAILS  ]================================
__authors__ = "Steve Tigrou"
__email__ = "user@gmail.com"
__copyright__ = "Copyright 2024, gestionnaire-site"
__date__ = "2024/06/21"
__version__ = "1.0.0"
__status__ = "Prototype"
# __status__ = "Production"
__description__ = "Gestion des sites vituels sur le serveur LAMP."
__credits__ = ["Steve Tigrou"]
__license__ = "GPU"
__maintainer__ = "Steve Tigrou"
__python__ = "3.12.3"
# ================================[ DOCSTRING ]================================
"""
Gestion des sites vituels sur le serveur LAMP
"""
# ================================[  HISTORY  ]================================
# 21/06/2024: Creation du projet
# ================================[ REFERENCE ]================================
# - https://www.w3schools.com/python/
# - Python Documentation
# ================================[  IMPORTS  ]================================
import os
import paramiko
import time
# ================================[  MODULES  ]================================


# ================================[ VARIABLES ]================================
HOSTNAME = "192.168.1.5"
PORT = 22
USER = "root"
PASSWORD = "tigger91220!"

DOMAINE = "mysf.ovh"
ADMIN_MAIL = "steve.tigrou@gmail.com"
PATH_CONF = "/etc/apache2/sites-available/"
PATH_CONF_FILE_APACHE = "/etc/apache2/apache2.conf"
PATH_SITES = "/var/www/"
FILE_INDEX = "index.html"
LARG_LIGNE = 57

site_name = ""
conf_file = ""
html_file = ""
# ================================[ FUNCTIONS ]================================


def clear_screen():
    """Efface le contenu du terminal / -> import os <-"""
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")


def client_connect_ssh(hostname: str, port: int, user: str, password: str)->object:
    """Connexion au serveur LAMP en ssh

    Args:
        hostname (str): Adresse IP du serveur
        port (int): Port de connexion ssh
        user (str): Nom du user
        password (str): Mot de passe du user

    Returns:
        object: Object de la connexion
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=user, password=password)
    return client


def start_script(instructions:str, code_use:str='script'):
    """Passeur de script dans la connexion ssh

    Args:
        instructions (str): commandes shell passé par la connexion
        code_use (str, optional): Code d'aiguillage. Defaults to 'script'.
                                    # code_use:
                                    # script   ->  utilisation par les scripts add et del
                                    # manuel   ->  utilisation pour des commandes manuel
                                    # listing  ->  recuperer la liste des sites en fonctionnement
    """
    try:
        ssh = client_connect_ssh(HOSTNAME, PORT, USER, PASSWORD)
        match code_use:
            case "script":
                for cmd in instructions:
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    # print(stdout.read().decode())
                stdin.close()
                print("FIN DU TRAITEMENT")
                time.sleep(5)
            case "manuel":
                while True:
                    try:
                        cmd = input("(exit) /> ")
                        if cmd == "exit": break
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        erreur = stderr.read().decode()
                        sortie = stdout.read().decode().split("\n")
                        if not erreur == "":
                            print(erreur)
                        else:
                            if len(sortie) == 1:
                                print(sortie)
                            else:
                                for out in sortie:
                                    #if not out == '':
                                    print(out)
                    except KeyboardInterrupt:
                        break
            case "listing":
                cmd = f'for i in {PATH_SITES}*/; do ls -d "$i"; done'
                stdin, stdout, stderr = ssh.exec_command(cmd)
                sortie = stdout.read().decode().split("\n")
                for out in sortie:
                    if not out == '':
                        out = out.replace(PATH_SITES, '')
                        out = out.replace('/', '')
                        print(f'    - http://{HOSTNAME}/{out}')
        ssh.close()
    except Exception as err:
        print(str(err))


def head_menu():
    """Constituer la tête du menu avec la liste des sites actifs
    """
    clear_screen()
    title = f"SITE APACHE {HOSTNAME}"
    nb_car_titre = len(title)
    espaces = (LARG_LIGNE-nb_car_titre)/2
    print(" " * int(espaces) + title)
    print("=" * LARG_LIGNE)
    print("  Liste des sites")
    start_script(None, "listing")
    print("=" * LARG_LIGNE)


# ================================[ PROGRAMME ]================================

while True:
        # génération du menu
        head_menu()
        print("  MENU")
        print("    0 - COMMANDE")
        print("    1 - AJOUTER")
        print("    2 - SUPPRIMER")
        print("    q - QUITTER")
        print("=" * LARG_LIGNE)
        choix = input(" /> ")
        head_menu()
        if choix == "1":
                # Demande du nom du nouveau site
            site_name = input("NOM DU SITE : ")
            if not site_name == "":
                conf_file = PATH_CONF + site_name + ".conf"
                html_file = PATH_SITES + site_name + "/" + FILE_INDEX
                # Liste des instructions pour ajouter un site
                addsite = (
                    f"mkdir {PATH_SITES + site_name}",
                    f"touch {conf_file}",
                    f'echo -e "<VirtualHost *:80>" >> {conf_file}',
                    f'echo -e "    #ServerAdmin {ADMIN_MAIL}" >> {conf_file}',
                    f'echo -e "    ServerName {site_name}.{DOMAINE}" >> {conf_file}',
                    f'echo -e "    ServerAlias www.{site_name}.{DOMAINE}" >> {conf_file}',
                    f'echo -e "    DocumentRoot {PATH_SITES + site_name}" >> {conf_file}',
                    'echo -e "    #ErrorLog ${APACHE_LOG_DIR}/'
                    + f'{site_name}/error.log" >> {conf_file}',
                    'echo -e "    #CustomLog ${APACHE_LOG_DIR}/'
                    + f'{site_name}/access.log combined" >> {conf_file}',
                    f'echo -e "</VirtualHost>" >> {conf_file}',
                    f'echo -e "Include {conf_file}" >> {PATH_CONF_FILE_APACHE}',
                    f"touch {html_file}",
                    f'echo -e "<!DOCTYPE html>" >> {html_file}',
                    f'echo -e "<html lang="fr">" >> {html_file}',
                    f'echo -e "    <head>" >> {html_file}',
                    f'echo -e "        <meta charset="UTF-8">" >> {html_file}',
                    f'echo -e "        <title>Bienvenue</title>" >> {html_file}',
                    f'echo -e "    </head>" >> {html_file}',
                    f'echo -e "    <body>" >> {html_file}',
                    f'echo -e "        <h1>La configuration pour {site_name}.{DOMAINE} fonctionne!</h1>" >> {html_file}',
                    f'echo -e "    </body>" >> {html_file}',
                    f'echo -e "</html>" >> {html_file}',
                )
                start_script(addsite, "script")
        elif choix == "2":
                # Demande du nom du site à supprimer
            site_name = input("NOM DU SITE : ")
            if not site_name == "":
                conf_file = PATH_CONF + site_name + ".conf"
                html_file = PATH_SITES + site_name + "/" + FILE_INDEX
                # Liste des instructions pour supprimer un site
                delsite = (
                    f'rm -r /var/www/{site_name}',
                    f'sed -i "/{site_name}.conf/d" {PATH_CONF_FILE_APACHE}',
                    f'rm -r {PATH_CONF}{site_name}.conf',
                )
                start_script(delsite, "script")
        elif choix == "0":
                # passer des commandes manuellement
            start_script(None, "manuel")
        elif choix == "q":
            break
