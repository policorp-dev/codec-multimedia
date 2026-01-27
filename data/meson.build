desktop_file = i18n.merge_file(
        input: 'org.gnome.CodecMultimedia.desktop.in',
       output: 'org.gnome.CodecMultimedia.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'org.gnome.CodecMultimedia.metainfo.xml.in',
       output: 'org.gnome.CodecMultimedia.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data('org.gnome.CodecMultimedia.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])


service_conf = configuration_data()
service_conf.set('bindir', get_option('prefix') / get_option('bindir'))
configure_file(
  input: 'org.gnome.CodecMultimedia.service.in',
  output: 'org.gnome.CodecMultimedia.service',
  configuration: service_conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)
configure_file(
  input: 'org.gnome.CodecMultimedia.Helper.service.in',
  output: 'org.gnome.CodecMultimedia.Helper.service',
  configuration: service_conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)
install_data('org.gnome.CodecMultimedia.policy',
	install_dir: get_option('datadir') / 'polkit-1' / 'actions'
)

subdir('icons')
