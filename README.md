# XAMPHP v1.0.2

**Project**: XAMPHP
<br>**Version**: 1.0.2
<br>**OS**: Microsoft / Windows
<br>**Author**: Irakli Gzirishvili
<br>**Mail**: gziraklirex@gmail.com

**XAMPHP** is a Python command-line interface application, designed to launch PHP projects via XAMPP engine from any location on your Windows machine as a virtual local host

## Installation

To use **XAMPHP**, follow these steps:

- Open CMD and run the following command to install `pip install xamphp` then restart your CMD
- To check if **XAMPHP** is installed correctly, run the following command `xamphp`

## Commands

These are the available commands you can use:

- `xamphp` - To list available commands
- `xamphp start (domain)` - Start the project with virtual domain
- `xamphp stop` - Stop the project if it didn't

## NOTE

- App will edit file 'C:/xampp/apache/conf/extra/httpd-vhosts.conf' to setup Virtual Host during execution.
- App will edit file 'C:/Windows/System32/drivers/etc/hosts' to map local IP address (127.0.0.1) to the Virtual Host.
- By default, app will reset these configurations after stopping the execution.

> You will need to use `Run as administrator` when using this app via CMD.
