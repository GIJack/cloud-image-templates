#!/usr/bin/env bash

SUBNET="172.16.15.0/24"
IFACE="eth0"

case ${1} in
 up)
  logger "OpenVPN Tunnel Rules UP"
  iptables -t nat -A POSTROUTING -s ${SUBNET} -o ${IFACE} -j MASQUERADE
  systemctl start dnsmasq.service
  ;;
 down)
  logger "OpenVPN Tunnel Rules DOWN"
  systemctl restart iptables
  systemctl stop dnsmasq.service
  ;;
 *)
  logger "Error setting up OpenVPN tunnel rules"
  ;;
esac

