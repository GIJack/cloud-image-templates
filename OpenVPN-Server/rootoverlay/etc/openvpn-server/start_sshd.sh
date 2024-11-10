#!/usr/bin/env bash

logger OpenVPN: starting sshd
systemctl restart sshd.service || logger OpenVPN failed to start sshd
