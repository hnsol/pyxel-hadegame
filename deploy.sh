pyxel package ./pyxelsg ./pyxelsg/pyxelsg.py
pyxel app2html pyxelsg.pyxapp
OLD="gamepad: \"enabled\""
NEW="gamepad: \"disabled\""
sed -i '' "s/${OLD}/${NEW}/g" ./pyxelsg.html
