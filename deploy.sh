pyxel package ./pyxelhg ./pyxelhg/main.py
#mv main.pyxapp pyxelhg.pyxapp
pyxel app2html pyxelhg.pyxapp
OLD="gamepad: \"enabled\""
NEW="gamepad: \"disabled\""
sed -i '' "s/${OLD}/${NEW}/g" ./pyxelhg.html
