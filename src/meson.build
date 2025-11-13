pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'codec_multimedia'
gnome = import('gnome')

gnome.compile_resources('codec-multimedia',
  'codec-multimedia.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)
conf.set('pkg_name', pkg_name)

configure_file(
  input: 'codec-multimedia.in',
  output: 'codec-multimedia',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

config_data_py = configuration_data()
config_data_py.set('pkg_name', pkg_name)
config_data_py.set('VERSION', meson.project_version())
config_data_py.set('pkgdatadir', pkgdatadir)

config_py = configure_file(
  input: 'config.py.in',
  output: 'config.py',
  configuration: config_data_py
)

codec_multimedia_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'codecs.txt',
  'install_apt.py',
  'uninstall_apt.py',
  'fingerprint.py',
  config_py,
]

install_data(codec_multimedia_sources, install_dir: moduledir)
