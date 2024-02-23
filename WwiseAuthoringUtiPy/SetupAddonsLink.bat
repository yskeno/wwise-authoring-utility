@echo off
setlocal enabledelayedexpansion
set AddonsFolder="%appdata%\Audiokinetic\Wwise\Add-ons\Commands\WwiseAuthoringUtility"
set SourceFolder="%~dp0WwiseAuthoringUtility

echo "*** Setup Command Add-ons in user data directory as junction link. ***"

if exist %AddonsFolder% (
echo "WwiseAuthoringUtility link couldn't be created."
echo "!AddonsFolder! folder already exists."
) else (
mklink /j !AddonsFolder! !SourceFolder!)

endlocal