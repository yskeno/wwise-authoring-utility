# Wwise Authoring Utility

## Requirements
* python 3.10+
* Wwise 2019.2.15+

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

## Usage
* Connect/Disconnect to Localhost
* Auto rename containers
* Auto assign switch containers

# Wwise Authoring Utility (Japanese)

## 必要条件
* python 3.10+
* Wwise 2019.2.15+

## セットアップ
1. Python3.10以上をインストールする。
2. コマンドプロンプトで以下のコマンドを実行し、PythonでWAAPIを使うための初期セットアップを完了する。\
参考: [Python (Waapi-Client) - Remote Procedure Call(プロジェクトの初期化)](https://www.audiokinetic.com/ja/public-library/2024.1.9_8920/?source=SDK&id=waapi_client_python_rpc.html#waapi_client_python_rpc_init)
	* Windows
		* py -3 -m pip install waapi-client
	* macOS, Linux
		* python3 -m pip install waapi-client
1. このリポジトリ全体をダウンロードもしくはクローンする。
2. リポジトリのうち、"Pythonフォルダ"と"WwiseUtility_Commands.json"を、以下のいずれかのWwiseコマンドアドオン階層にコピーする。\
   もしフォルダが存在しない場合は、新規で作成してからコピーする。
	* ユーザデータディレクトリ内の階層(インストール済みのWwiseすべてで使用する場合の階層):
		* Windows: %APPDATA%\Audiokinetic\Wwise\Add-ons\Commands
	* Installationフォルダ内の階層(特定のWwiseバージョンに限定して使用する場合の階層):
		* Windows: %WWISEROOT%\Authoring\Data\Add-ons\Commands
	* プロジェクトフォルダ内の、"Add-ons\Commands"以下(特定のwprojに限定して使用する場合の階層)
4. Wwiseを起動する。
