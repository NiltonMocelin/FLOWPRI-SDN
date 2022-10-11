ovs <v2.12 nao suporta kernel mais novo que 4.9x

Entao, baixei :wget kernel.ubuntu.com/~kernel-ppa/mainline/v4.9/linux-headers-4.9.0-040900_4.9.0-040900.201612111631_all.deb

--> [ovs v2.13.1] estou usando um kernel mais novo atualmente v5.x.

Caso o ovsdb nao esteja iniciando:
em modo: sudo su
export PATH=$PATH:/usr/local/share/openvswitch/scripts
ovs-ctl restart

** pois nao eh possivel usar sudo com ovs-ctl, teria que ir na pastas sudo /sla/naosei/ovs-ctl
** sem sudo, nao consegue iniciar ovsdb data base, algo assim.
