build:
	pyinstaller cli.py --name "lol-announcer" --add-binary announcer/sounds:announcer/sounds

clean:
	rm -rf lol-announcer.spec build/ dist/
