. $(dirname $0)/config.inc

cd $(dirname $0)/../ > /dev/null 2>&1

if ! test "$USER" = "www-data" && ! test "$PRODOUANE_NO_WWWDATA" ; then
    printf "ERROR :\tl'utilisateur n'est pas www-data\n"
    printf "\tla variable d'environnement PRODOUANE_NO_WWWDATA permet de désactiver cette sécurité\n"

    exit 1
fi
