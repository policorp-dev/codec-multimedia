application_id = 'org.gnome.CodecMultimedia'

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)

#symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
# 1. Crie uma lista com todos os ícones simbólicos que você quer instalar
#symbolic_icons = [
#  symbolic_dir / ('@0@-symbolic.svg').format(application_id),
#  symbolic_dir / 'codec-icon-symbolic.svg'
#]

scalable_dir = 'hicolor' / 'scalable' / 'apps'
# 1. Crie uma lista com todos os ícones simbólicos que você quer instalar
scalable_icons = [
  scalable_dir / ('@0@.svg').format(application_id),
  scalable_dir / 'play-button-svgrepo-com.svg',
  scalable_dir / 'logo-policorp-codec.png'
]

install_data(
  scalable_icons,
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

#install_data(
#  symbolic_icons,
#  install_dir: get_option('datadir') / 'icons' / symbolic_dir
#)
logo_install_path = get_option('datadir') / 'icons' / scalable_dir