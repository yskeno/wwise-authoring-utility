# Wwise Authoring Utility

## Requirements
* python 3.10 - 3.13
* Wwise 2019.2.15+

## Functions
* Connect/Disconnect to Localhost without opening RemoteConnection dialog.
![WAU_ConnectToLocalhost-ezgif](https://github.com/user-attachments/assets/3a10d16f-ef84-4f2d-a41b-0cfd9a4ca730)

* Create Rondom/Sequence/Blend/Switch container(s) with selected objects.\
  It supports asset names with numeric suffixes.
![WAU_CreateContainer-ezgif](https://github.com/user-attachments/assets/57e77f2d-305a-45d1-a8f4-1cb17ff8a6a4)

* Auto assign objects to switch in Switch Container.\
  It supports asset names structured as "common string" + "switch name" + "optional numeric suffix".
![WAU_AssignSwitch-ezgif](https://github.com/user-attachments/assets/1a7a4779-3872-4417-b575-5af91ed834ed)

\
****English version below.***
## セットアップ
1. Python3.10 ～ 3.13のいずれかをインストールする。
1. コマンドプロンプトで以下のコマンドを実行し、PythonでWAAPIを使うための初期セットアップを完了する。[^1]\
参考: [Python (Waapi-Client) - Remote Procedure Call(プロジェクトの初期化)](https://www.audiokinetic.com/ja/public-library/2024.1.9_8920/?source=SDK&id=waapi_client_python_rpc.html#waapi_client_python_rpc_init)
	* Windows
		* py -3 -m pip install waapi-client
1. このリポジトリ全体をダウンロードもしくはクローンする。
1. リポジトリのうち、"Pythonフォルダ"と"WwiseUtility_Commands.json"を、以下のいずれかのWwiseコマンドアドオン階層にコピーする。\
   もしフォルダが存在しない場合は、新規で作成してからコピーする。
	* ユーザデータディレクトリ内の階層(インストール済みのWwiseすべてで使用する場合の階層):
		* Windows: %APPDATA%\Audiokinetic\Wwise\Add-ons\Commands
	* Installationフォルダ内の階層(特定のWwiseバージョンに限定して使用する場合の階層):
		* Windows: %WWISEROOT%\Authoring\Data\Add-ons\Commands
	* プロジェクトフォルダ内の、"Add-ons\Commands"以下(特定のwprojに限定して使用する場合の階層)
1. Wwiseを起動して、任意のプロジェクトを開く。
1. 上部のメインメニューもしくは各オブジェクトを右クリックしたメニュー内にあるWwiseUtilityから使いたい機能を選べばOK :+1:

## SetUp
### Using EXE
1. Download WwiseAuthoringUtility_v*.*.zip from release page.
1. Extract downloaded zip file.
1. Move extracted files to following directory.
	* User data directory:
		* Windows: "%APPDATA%\\Audiokinetic\\Wwise\\Add-ons\\Commands"
		* macOS: "$HOME/Library/Application Support/Audiokinetic/Wwise/Add-ons/Commands"
	* Installation folder:
		* Windows: "%WWISEROOT%\\Authoring\\Data\\Add-ons\\Commands"
		* macOS: "/Library/Application Support/Audiokinetic/Wwise <version>/Authoring/Data/Add-ons/Commands"
	* Project folder:
		* "Add-ons\\Commands"
1. Relaunch Wwise or reload command add-ons.

[^1]: [Python (Waapi-Client) - Remote Procedure Call(プロジェクトの初期化)](https://www.audiokinetic.com/ja/public-library/2024.1.9_8920/?source=SDK&id=waapi_client_python_rpc.html#waapi_client_python_rpc_init)
