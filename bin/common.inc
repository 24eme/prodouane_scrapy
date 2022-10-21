LANG=fr_FR.UTF-8

if ! test "$PRODOUANE_CONFIG_FILENAME"; then
PRODOUANE_CONFIG_FILENAME="config.inc"
fi

if test -d $(dirname $0)/../pyenv ; then
    source $(dirname $0)/../pyenv/bin/activate
fi

if ! test -f $(dirname $0)/$PRODOUANE_CONFIG_FILENAME ; then
    printf "ERROR:\tfichier de configuration ("$(dirname $0)"/"$PRODOUANE_CONFIG_FILENAME") non présent\n"
    printf "\tle nom du fichier est pesonnalisable via la variable de configuration PRODOUANE_CONFIG_FILENAME (par defaut config.inc)\n"
    exit 1;
fi

. $(dirname $0)/$PRODOUANE_CONFIG_FILENAME

cd $(dirname $0)/../ > /dev/null 2>&1

if ! test "$USER" && test "$APACHE_RUN_USER"; then
    USER=$APACHE_RUN_USER
fi

if ! test "$USER" = "www-data" && ! test "$PRODOUANE_NO_WWWDATA" ; then
    printf "ERROR :\tl'utilisateur n'est pas www-data\n"
    printf "\tla variable d'environnement PRODOUANE_NO_WWWDATA permet de désactiver cette sécurité\n"
    exit 2
fi
