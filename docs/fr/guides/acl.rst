Gestion des droits d'accès sous ZORNA
*************************************

ZORNA utilise les groupes pour gérer les droits sur les objets. Un groupe est un ensemble d'utilisateurs enregistrés dans la base de données. Les groupes sont hiérarchiques c'est à dire organisés sous forme d'arborescence.

Chaque objet a des droits spécifiques. Ainsi pour un objet on peut octroyer un droit de lecture ou de création alors que pour un autre on utilise plutôt un droit d'accès ou tout autre.

Tous les membres d'un groupe bénéficient des droits octroyés à un groupe.

Pour éviter inutilement la création de groupes, ZORNA permet d'octroyer des droits par utilisateur.

Un droit peut être accordé à un groupe ou au groupe et à ses descendants.

De la même manière un droit peut être refusé à un groupe ou à ses descendants.

On peut accorder un droit à un groupe et ses descendants et le refuser pour quelques groupes dans la hiérarchie.

Cette façon de gérer les droits évite la multiplication des groupes et offre beaucoup plus de souplesse.

Les autorisations de droit pour un groupe sont:

* **Allow**: pour autoriser le droit au groupe
* **Allow++**: pour autoriser le droit au groupe et à ses descendants
* **Deny**: pour refuser le droit au groupe
* **Deny++**: pour refuser le droit au groupe et à ses descendants

Les autorisations d'un droit pour un utilisateur sont:

* **Allow:** pour autoriser le droit à l'utilisateur
* **Deny**: pour refuser le droit