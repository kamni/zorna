################################
Management of Access Permissions
################################

********
Preamble
********

ZORNA use groups to manage permissions on objects. A group is a set of users
registered in the database. Groups are hierarchical -- i.e., organized as a
tree.

To grant permissions to an object managed by ZORNA (article, faq, file, etc...),
you can specify either 'allow' or 'deny' permissions for a group. All members
of a group have the permissions granted to that group.

To avoid unnecessarily creating groups, ZORNA also lets you grant user-level
rights.

An 'allow' permission may be granted either to a group, or to the group and its
sub-groups.

Similarly, a permission may be denied to a group or its sub-groups.

You may grant access to one group and its subgroups while denying permission
for some groups in the hierarchy.

This way of managing rights avoids creating too many groups and offers a lot
more flexibility.

******
Groups
******

ZORNA allows for organizing groups in a hierarchical manner:

.. image:: ../../images/adm-groupes.png

To create a group, as an administrator, click on the link
"Administration -> Groups" then "Add Group".

To see the members of a group or to add members to a group, click the "Members"
icon.

******************
Object Permissions
******************

Each object has its own permissions. So for one object you can grant
permissions to read or edit it, and then use another set of permissions for
different object.

The access permissions for groups are:

* **Allow**: to add access for the group
* **Allow++**: to add access for the group and its sub-groups
* **Deny**: to remove access for the group
* **Deny++**: to remove access for the group and its sub-groups

The access permissions for individual users are:

* **Allow:** to add access for a user
* **Deny**: to remove access

.. image:: ../../images/adm-rights.png

***********************
Duplicating permissions
***********************

Granting permissions to an object can easily become tedious, especially if the
number of groups is very large.

To avoid this, ZORNA allows you to duplicate the permissions of an object and
to apply those permissions to another object.

Just create the new object and go to screen for setting permissions. On this
screen, scroll to the listbox "Load permissions from" to load the permissions
from another object. ZORNA will apply the  granted to the object to apply the new object. Save to save the new rights.
Pour cela il suffit de créer le nouvel objet et d'aller à l'interface de création des droits. Sur cette interface, déroulez la listbox "Charger les permissions à partir de" pour charger les permissions à partir d'un autre objet. ZORNA charge les droits octroyés à l'objet pour les appliquer au nouvel objet.
Enregistrer pour sauvegarder les nouveaux droits.