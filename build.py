import PyInstaller.__main__
from pathlib import Path

desktop = str(Path.home()) + '/Desktop' # 取得桌面路径

PyInstaller.__main__.run([
    'main.py',
    '--add-data=./*.py;.',
    '--add-data=./assets/*.json;.',
    '--add-data=./assets/tiles/*.png;.',
    '--add-data=./assets/entitys/player/idle/*.png;.',
    '-n=走格子',
    '-w',
    '-i=oh.ico',
    '-y',
    '--distpath=' + str(desktop) + '/codemao/dist',  # 指定应用程序输出目录为桌面-codemao-dist
    '--workpath=' + str(desktop) + '/codemao/build',  # 指定过程生成文件位于桌面-codemao-build

])
