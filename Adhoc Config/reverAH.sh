#Recuperamos la configuración inicial
cp /etc/network/interfaces_backup /etc/network/interfaces

#Reiniciamos el servicio de red para aplicar los cambios
service networking restart
sudo reboot