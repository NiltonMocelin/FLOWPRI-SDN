#http://www.openvswitch.org/support/dist-docs/ovs-fields.7.txt


Entao, para verificar se o campo TOS esta settado, quando um pacote chega na primeira tabela, pode-se utilizar de alguns artificios:
nw_tos


*- Wildcard, e.g. ``any nw_src’’
                     The  value  of  the  field is not constrained. Wildcarded  fields may be written as field=*, although it is  unusual to  mention  them at all. (When specifying a wildcard explicitly in a command invocation, be sure to using  quoting to protect against shell expansion.)

                     There  is  a  tiny difference between wildcarding a field and not specifying any match on a  field:  wildcarding  a field requires satisfying the field’s prerequisites.
 |-> pelo que entendi, o campo precisa existir e estar settado



*- Inequality match, e.g. ``tcp_dst ≠ 80’’
                     The value of the field differs from  a  specified  value, for example, all TCP destination ports except 80.

                     An inequality match on an n-bit field can be expressed as a disjunction of n 1-bit matches. For  example,  the  in equality  match  ``vlan_pcp  ≠  5’’  can  be expressed as ``vlan_pcp = 0/4 or vlan_pcp = 2/2 or vlan_pcp  =  0/1.’’

                     For  matches  used in flows (see Flows, below), sometimes one can more compactly express inequality  as  a  higher-priority  flow  that  matches the exceptional case paired with a lower-priority flow that matches the general case.

                     Alternatively, an inequality match may be converted to  a pair of range matches, e.g. tcp_src ≠ 80 may be expressed as ``0 ≤ tcp_src < 80 or 80 < tcp_src ≤ 65535’’, and then each  range  match  may in turn be converted to a bitwise match.
