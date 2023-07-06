#!/bin/bash

mv ../go.work ../_go.work
cd ../packages/assets
gopy build -output=assets -vm=python assets
rm -r ../plugin/assets
mv assets ../plugin/assets
cd ../../
mv _go.work go.work
