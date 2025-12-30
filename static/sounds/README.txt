# 音声ファイル生成スクリプト
# 実際の音声ファイルはユーザーが用意するか、以下のコマンドで生成できます

# Windowsの場合、PowerShellで簡単なビープ音を生成する方法:
# [console]::beep(800, 500)  # 有効音: 800Hz, 500ms
# [console]::beep(400, 500)  # 無効音: 400Hz, 500ms

# または、オンラインの音声生成ツールを使用して
# valid.mp3 (高めの音)
# invalid.mp3 (低めの音)
# を作成し、static/sounds/ に配置してください

print("音声ファイルは static/sounds/ に配置してください")
print("valid.mp3 - 有効時の音声")
print("invalid.mp3 - 無効時の音声")
