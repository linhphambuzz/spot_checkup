#!/bin/bash

waitress-serve --port 5000 --call "main:create_app"
