#Copia de la configuración actual
cp /etc/network/interfaces /etc/network/interfaces_backup

#Configuramos adhoc en el fichero de configuración
cp confAdhoc_2 /etc/network/interfaces

#Reiniciamos el servicio de red para aplicar los cambios
service networking restart
sudo reboot