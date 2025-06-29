#!/bin/bash
echo "Installing wkhtmltopdf..."

curl -L -o wkhtmltox.tar.xz https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox-0.12.6-1.amd64.tar.xz
tar -xf wkhtmltox.tar.xz
sudo mv wkhtmltox*/bin/wkhtmlto* /usr/bin/
