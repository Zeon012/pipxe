Quick install / deploy notes

1. Copy files to your Raspberry Pi and install into `/opt/pipxe`:

```bash
# from this repo (example)
scp -r gadget_cdrom pi@pi:~/
# on the Pi
sudo mkdir -p /opt/pipxe
sudo rsync -a ~/gadget_cdrom/ /opt/pipxe/
```

2. Install helper scripts to `/usr/local/bin`:

```bash
sudo install -m 0755 /opt/pipxe/pxe.sh /usr/local/bin/pxe.sh
sudo install -m 0755 /opt/pipxe/mode.sh /usr/local/bin/mode.sh
sudo install -m 0755 /opt/pipxe/list_pxe.sh /usr/local/bin/list_pxe.sh
```

3. Ensure Python and system deps are installed:

```bash
sudo apt update
sudo apt install -y dnsmasq python3-pil python3-rpi.gpio python3-spidev fonts-dejavu-core
```

4. Start PXE on the Pi (example):

```bash
sudo /usr/local/bin/pxe.sh start /pxe/example.ipxe
```

