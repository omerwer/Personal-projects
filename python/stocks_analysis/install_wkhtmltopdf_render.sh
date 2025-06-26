#!/bin/bash
# Install wkhtmltopdf static build
echo "Installing wkhtmltopdf..."
curl -L -o wkhtmltox.tar.xz https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.amd64.tar.xz
tar -xf wkhtmltox.tar.xz
mv wkhtmltox*/bin/wkhtmlto* /usr/bin/
