@echo off
chcp 65001 > nul
title pksl diary - View on Phone
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve-for-phone.ps1"
