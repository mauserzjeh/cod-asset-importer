#!/bin/bash

mv ../go.work ../_go.work
cd ../packages/importer
gopy build -output=importer -vm=python importer
rm -r ../plugin/importer
mv importer ../plugin/importer
cd ../../
mv _go.work go.work
